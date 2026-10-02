"""Small dependency-free PDF generator for prediction reports."""

from datetime import datetime
from pathlib import Path
import struct
import zlib


PAGE_WIDTH = 595
PAGE_HEIGHT = 842
LEFT = 46
RIGHT = PAGE_WIDTH - LEFT
NAVY = (0.09, 0.22, 0.43)
BLUE = (0.20, 0.39, 0.69)
INK = (0.16, 0.22, 0.31)
MUTED = (0.39, 0.45, 0.54)
LINE = (0.86, 0.89, 0.93)


def _safe_text(value):
    value = str(value or "")
    return value.encode("cp1252", "replace").decode("cp1252")


class _Page:
    def __init__(self):
        self.commands = []

    @staticmethod
    def _color(color):
        return " ".join(f"{part:.3f}" for part in color)

    def rect(self, x, y, width, height, fill, stroke=None):
        if fill:
            self.commands.append(f"{self._color(fill)} rg")
        if stroke:
            self.commands.append(f"{self._color(stroke)} RG 0.7 w")
        self.commands.append(f"{x:.1f} {y:.1f} {width:.1f} {height:.1f} re {'B' if fill and stroke else 'f' if fill else 'S'}")

    def line(self, x1, y1, x2, y2, color=LINE, width=0.7):
        self.commands.append(f"{self._color(color)} RG {width:.1f} w {x1:.1f} {y1:.1f} m {x2:.1f} {y2:.1f} l S")

    def text(self, x, y, value, size=9, color=INK, bold=False):
        font = "F2" if bold else "F1"
        value = _safe_text(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        self.commands.append(f"{self._color(color)} rg BT /{font} {size:.1f} Tf 1 0 0 1 {x:.1f} {y:.1f} Tm ({value}) Tj ET")

    def image(self, x, y, width, height):
        self.commands.append(f"q {width:.1f} 0 0 {height:.1f} {x:.1f} {y:.1f} cm /Im1 Do Q")

    def bytes(self):
        return "\n".join(self.commands).encode("cp1252", "replace")


def _wrap(value, max_chars):
    words = _safe_text(value).split()
    lines, current = [], ""
    for word in words:
        if current and len(current) + len(word) + 1 > max_chars:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return lines or [""]


def _read_rgba_png(path):
    """Read an 8-bit RGBA PNG and return PDF-ready RGB and alpha streams."""
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("EduGuide logo must be a PNG image.")
    width = height = bit_depth = color_type = None
    compressed = bytearray()
    offset = 8
    while offset < len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        chunk = data[offset + 8:offset + 8 + length]
        offset += 12 + length
        if kind == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(">IIBB", chunk[:10])
        elif kind == b"IDAT":
            compressed.extend(chunk)
        elif kind == b"IEND":
            break
    if bit_depth != 8 or color_type != 6:
        raise ValueError("EduGuide logo must use 8-bit RGBA color.")

    raw = zlib.decompress(compressed)
    stride = width * 4
    previous = bytearray(stride)
    rgb_rows, alpha_rows = bytearray(), bytearray()

    def paeth(left, above, upper_left):
        estimate = left + above - upper_left
        distances = (abs(estimate - left), abs(estimate - above), abs(estimate - upper_left))
        return (left, above, upper_left)[distances.index(min(distances))]

    cursor = 0
    for _ in range(height):
        filter_type = raw[cursor]
        scan = bytearray(raw[cursor + 1:cursor + 1 + stride])
        cursor += stride + 1
        for index in range(stride):
            left = scan[index - 4] if index >= 4 else 0
            above = previous[index]
            upper_left = previous[index - 4] if index >= 4 else 0
            if filter_type == 1:
                scan[index] = (scan[index] + left) & 255
            elif filter_type == 2:
                scan[index] = (scan[index] + above) & 255
            elif filter_type == 3:
                scan[index] = (scan[index] + ((left + above) // 2)) & 255
            elif filter_type == 4:
                scan[index] = (scan[index] + paeth(left, above, upper_left)) & 255
            elif filter_type != 0:
                raise ValueError("Unsupported PNG filter in EduGuide logo.")
        for index in range(0, stride, 4):
            rgb_rows.extend(scan[index:index + 3])
            alpha_rows.append(scan[index + 3])
        previous = scan
    return width, height, zlib.compress(rgb_rows), zlib.compress(alpha_rows)


def _make_pdf(pages, logo_path):
    width, height, rgb_stream, alpha_stream = _read_rgba_png(logo_path)
    image_id = 5 + 2 * len(pages)
    alpha_id = image_id + 1
    objects = [b""] * (4 + 2 * len(pages) + 2)
    page_refs = " ".join(f"{5 + 2 * i} 0 R" for i in range(len(pages)))
    objects[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects[1] = f"<< /Type /Pages /Kids [{page_refs}] /Count {len(pages)} >>".encode("ascii")
    objects[2] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
    objects[3] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"
    for index, page in enumerate(pages):
        page_id = 5 + 2 * index
        stream_id = page_id + 1
        stream = page.bytes()
        objects[page_id - 1] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> /XObject << /Im1 {image_id} 0 R >> >> "
            f"/Contents {stream_id} 0 R >>"
        ).encode("ascii")
        objects[stream_id - 1] = f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"\nendstream"
    objects[image_id - 1] = (
        f"<< /Type /XObject /Subtype /Image /Width {width} /Height {height} "
        f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /SMask {alpha_id} 0 R "
        f"/Length {len(rgb_stream)} >>\nstream\n"
    ).encode("ascii") + rgb_stream + b"\nendstream"
    objects[alpha_id - 1] = (
        f"<< /Type /XObject /Subtype /Image /Width {width} /Height {height} "
        f"/ColorSpace /DeviceGray /BitsPerComponent 8 /Filter /FlateDecode "
        f"/Length {len(alpha_stream)} >>\nstream\n"
    ).encode("ascii") + alpha_stream + b"\nendstream"

    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for object_id, body in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{object_id} 0 obj\n".encode("ascii"))
        output.extend(body)
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode("ascii"))
    return bytes(output)


def build_prediction_pdf(report):
    """Render a formal A4 report following the user's supplied report layout."""
    profile = report["profile"]
    results = report["results"]
    bands = (("high", "High chance", (0.56, 0.70, 0.57)),
             ("good", "Good chance", (0.49, 0.63, 0.80)),
             ("moderate", "Moderate chance", (0.77, 0.69, 0.49)),
             ("stretch", "Stretch option", (0.68, 0.61, 0.75)))
    counts = {level: sum(1 for result in results if result["level"] == level) for level, _, _ in bands}
    pages = []
    report_date = datetime.now().strftime("%d %B %Y")
    years = ", ".join(str(year) for year in report.get("data_years", [])) or "Not available"

    def footer(current_page):
        page.line(LEFT, 35, RIGHT, 35)
        page.text(LEFT, 21, "EduGuide  |  Smart Admission Guidance System", 7, MUTED)
        page.text(RIGHT - 50, 21, f"Page {current_page}", 7, MUTED)

    # Page 1: centered title, report context, applicant profile and prediction summary.
    page = _Page()
    page.image(224, 799, 32, 27.7)
    page.text(265, 807, "EDUGUIDE", 19, NAVY, True)
    page.text(205, 788, "SMART ADMISSION GUIDANCE SYSTEM", 8, MUTED)
    page.text(155, 757, "COLLEGE PREDICTION REPORT", 17, NAVY, True)
    page.text(239, 739, f"Generated: {report_date}", 8, MUTED)

    note_text = (
        "This report provides an estimated list of colleges based on the student’s academic profile, selected "
        "preferences, and historical cutoff data available in EduGuide. The predictions are for guidance purposes "
        "only and do not guarantee admission, allotment, eligibility, or seat availability. Students are advised "
        "to verify the latest admission information from the official DTE Maharashtra portal."
    )
    note_lines = _wrap(note_text, 120)
    note_top = 726
    note_line_height = 12
    note_first_baseline = note_top - 35
    note_bottom_padding = 14
    note_bottom = note_first_baseline - (len(note_lines) - 1) * note_line_height - note_bottom_padding
    page.rect(LEFT, note_bottom, RIGHT - LEFT, note_top - note_bottom, (0.98, 0.99, 1), (0.77, 0.84, 0.94))
    page.text(LEFT + 10, note_top - 15, "Note", 8, NAVY, True)
    for line_index, line in enumerate(note_lines):
        page.text(LEFT + 10, note_first_baseline - line_index * note_line_height, line, 8, INK)

    def table(title, y, rows, left_header, right_header, row_height=21):
        page.text(LEFT + 7, y + 12, title, 11, NAVY, True)
        table_top = y - 2
        page.rect(LEFT, table_top - 21, RIGHT - LEFT, 21, (0.91, 0.945, 0.99), LINE)
        page.text(LEFT + 7, table_top - 14, left_header, 7.5, NAVY, True)
        page.text(LEFT + 218, table_top - 14, right_header, 7.5, NAVY, True)
        page.line(LEFT + 205, table_top - 21, LEFT + 205, table_top - 21 - row_height * len(rows), LINE)
        current_y = table_top - 21
        for label, value in rows:
            page.rect(LEFT, current_y - row_height, RIGHT - LEFT, row_height, (1, 1, 1), LINE)
            page.text(LEFT + 7, current_y - 14, label, 7.5, INK)
            page.text(LEFT + 218, current_y - 14, _wrap(value, 58)[0], 7.5, INK)
            current_y -= row_height
        return current_y

    profile_rows = [
        ("Applicant", profile.get("name", "Student applicant")),
        ("Academic Score", f"{profile['percentage']}%"),
        ("Reservation Category", profile["category"]),
        ("Preferred Branch", profile["branch"]),
        ("Preferred Location", profile.get("location", "Any")),
        ("College Type", profile.get("college_type", "Any")),
        ("Admission Year", str(profile["admission_year"])),
    ]
    profile_bottom = table("1. Applicant Profile", note_bottom - 36, profile_rows, "Field", "Applicant Information")
    summary_rows = [
        ("Colleges matched", str(len(results))),
        ("Strongest match score", f"{max((r['confidence'] for r in results), default=0)}%"),
        ("Cutoff data considered", years),
        ("Report generated", report_date),
    ]
    summary_bottom = table("2. Prediction Summary", profile_bottom - 27, summary_rows, "Measure", "Result")

    footer(1)
    pages.append(page)

    # Page 2 onward: individual predicted college records.
    def start_matches_page(continued=False):
        nonlocal page
        page = _Page()
        page.text(LEFT, 806, "EduGuide", 17, NAVY, True)
        page.text(LEFT, 788, "COLLEGE PREDICTION REPORT", 7, MUTED, True)
        page.text(RIGHT - 122, 806, report_date, 8, MUTED)
        page.line(LEFT, 772, RIGHT, 772)
        heading = "3. Predicted College Matches" + (" (continued)" if continued else "")
        page.text(LEFT, 743, heading, 16, NAVY, True)
        page.text(LEFT, 725, f"{profile['branch']}  |  {profile['percentage']}%  |  {profile['category']}  |  Historical data: {years}", 8, MUTED)
        page.line(LEFT, 710, RIGHT, 710)
        return 690

    y = start_matches_page()
    for index, result in enumerate(results, start=1):
        name_lines = _wrap(result["college"], 57)
        page_bottom_limit = 95 if index == len(results) else 55
        if y - (104 + max(0, len(name_lines) - 1) * 11) < page_bottom_limit:
            footer(len(pages) + 1)
            pages.append(page)
            y = start_matches_page(continued=True)
        height = 98 + max(0, len(name_lines) - 1) * 11
        page.rect(LEFT, y - height, RIGHT - LEFT, height, (1, 1, 1), LINE)
        level_color = next((color for level, _, color in bands if level == result["level"]), BLUE)
        page.rect(LEFT, y - 19, 3, 19, level_color)
        page.text(LEFT + 12, y - 15, f"{index:02d}  {name_lines[0]}", 10, NAVY, True)
        for line_index, line in enumerate(name_lines[1:], start=1):
            page.text(LEFT + 31, y - 15 - 11 * line_index, line, 9, NAVY, True)
        top_offset = 15 + max(0, len(name_lines) - 1) * 11
        page.text(LEFT + 12, y - top_offset - 14, f"{result['location']}  |  {result['course']}", 8, MUTED)
        page.text(LEFT + 12, y - top_offset - 28, f"{result['chance']}  |  {result['college_type']}", 8, INK, True)
        page.text(LEFT + 12, y - top_offset - 41, f"Eligible cutoff: {result['cutoff']}%  |  Your margin: {result['margin']:+}%  |  {result['records_used']} records", 7.5, MUTED)
        page.text(LEFT + 12, y - top_offset - 54, "Prediction explanation: compared with the most competitive eligible historical cutoff for this course.", 7, MUTED)
        official_site = result.get("official_website") or "Verify through the official DTE institute listing"
        official = f"Institute code: {result.get('college_code') or 'Not listed'}  |  Official information: {official_site}"
        for line_index, line in enumerate(_wrap(official, 79)[:2]):
            page.text(LEFT + 12, y - top_offset - 68 - line_index * 9, line, 6.5, BLUE)
        page.text(RIGHT - 92, y - 16, f"{result['confidence']}%", 13, NAVY, True)
        page.text(RIGHT - 91, y - 29, "MATCH SCORE", 6, MUTED, True)
        y -= height + 7

    if not results:
        page.text(LEFT, y - 12, "No colleges matched this profile using the available cutoff records.", 9, MUTED)
    closing = "All the Best for Your Admission Journey"
    page.text((PAGE_WIDTH - len(closing) * 4.8) / 2, 53, closing, 9, NAVY, True)
    footer(len(pages) + 1)
    pages.append(page)

    logo_path = Path(__file__).resolve().parent.parent / "static" / "images" / "EduGuide Logo.png"
    return _make_pdf(pages, logo_path)

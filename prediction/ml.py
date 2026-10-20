"""Small, data-driven cutoff regression helpers.

The available cutoff history is short, so ordinary least-squares linear
regression is used and only returned when at least two admission years exist.
"""

import re


def _year_number(value):
    match = re.search(r"\d{4}", str(value or ""))
    return int(match.group()) if match else None


def _next_admission_year(value):
    years = re.findall(r"\d{4}", str(value or ""))
    if not years:
        return "the next admission year"
    start = int(years[0]) + 1
    end = int(years[1]) + 1 if len(years) > 1 else start + 1
    return f"{start}-{str(end)[-2:]}"


def predict_next_cutoff(records, through_year=None):
    """Fit OLS to annual mean cutoff percentages and extrapolate one year."""
    records = list(records)
    annual = {}
    for year, percentage_fraction in records:
        year_number = _year_number(year)
        if year_number is None or percentage_fraction is None:
            continue
        if through_year and year_number > through_year:
            continue
        # The legacy DB column is named cutoff_percentile, but the source
        # values are percentages stored as fractions (for example, 0.78).
        annual.setdefault(year_number, []).append(float(percentage_fraction) * 100)

    points = sorted((year, sum(values) / len(values)) for year, values in annual.items())
    if len(points) < 2:
        return None

    # Center x to keep the least-squares calculation numerically stable.
    mean_x = sum(year for year, _ in points) / len(points)
    mean_y = sum(value for _, value in points) / len(points)
    denominator = sum((year - mean_x) ** 2 for year, _ in points)
    if not denominator:
        return None
    slope = sum((year - mean_x) * (value - mean_y) for year, value in points) / denominator
    prediction = max(0.0, min(100.0, mean_y + slope * (points[-1][0] + 1 - mean_x)))
    last_year_text = next((str(year) for year, _ in records if _year_number(year) == points[-1][0]), str(points[-1][0]))
    return {
        "percentage": round(prediction, 2),
        "admission_year": _next_admission_year(last_year_text),
        "history_years": len(points),
        "model": "Linear regression",
    }

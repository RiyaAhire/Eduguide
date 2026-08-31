import pandas as pd
from pathlib import Path

base_path = Path("data/2025-26/cutoff")

for excel_file in base_path.rglob("*.xlsx"):
    csv_file = excel_file.with_suffix(".csv")

    df = pd.read_excel(excel_file)
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")

    print(f"Converted: {excel_file.name}")
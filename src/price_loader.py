from __future__ import annotations

from io import BytesIO
from pathlib import Path
import zipfile

import pandas as pd


def load_dispatch_prices(prices_dir: Path | str = Path("data/prices")) -> pd.DataFrame:
    """Load AEMO dispatch PRE_AP price rows from nested daily ZIP files.

    Returns a DataFrame with columns: timestamp, region, price.
    """
    prices_path = Path(prices_dir)
    if not prices_path.exists():
        raise FileNotFoundError(f"Prices directory not found: {prices_path}")

    frames: list[pd.DataFrame] = []
    daily_files_processed = 0
    nested_files_processed = 0
    total_rows_loaded = 0

    for daily_zip_path in sorted(prices_path.glob("*.zip")):
        daily_files_processed += 1
        with zipfile.ZipFile(daily_zip_path, "r") as outer_zip:
            nested_zip_names = [
                name
                for name in outer_zip.namelist()
                if name.lower().endswith(".zip") and not name.endswith("/")
            ]

            for nested_zip_name in nested_zip_names:
                with outer_zip.open(nested_zip_name) as nested_file:
                    nested_bytes = nested_file.read()

                with zipfile.ZipFile(BytesIO(nested_bytes), "r") as inner_zip:
                    csv_names = [
                        name
                        for name in inner_zip.namelist()
                        if name.lower().endswith(".csv") and not name.endswith("/")
                    ]
                    if not csv_names:
                        continue

                    with inner_zip.open(csv_names[0]) as csv_file:
                        # AEMO files mix C/I/D row shapes; set a fixed width to parse all rows.
                        df = pd.read_csv(
                            csv_file, header=None, names=range(15), engine="python"
                        )

                data_rows = df[df[0] == "D"].loc[:, [4, 5, 6]].copy()
                data_rows.columns = ["timestamp", "region", "price"]
                frames.append(data_rows)

                nested_files_processed += 1
                total_rows_loaded += len(data_rows)

    result = (
        pd.concat(frames, ignore_index=True)
        if frames
        else pd.DataFrame(columns=["timestamp", "region", "price"])
    )

    if not result.empty:
        result["timestamp"] = pd.to_datetime(result["timestamp"], errors="coerce")
        result["price"] = pd.to_numeric(result["price"], errors="coerce")

    print(f"number of files processed: {nested_files_processed}")
    print(f"daily zip files processed: {daily_files_processed}")
    print(f"total rows loaded: {total_rows_loaded}")

    return result


if __name__ == "__main__":
    dispatch_prices = load_dispatch_prices()
    print(dispatch_prices.head())

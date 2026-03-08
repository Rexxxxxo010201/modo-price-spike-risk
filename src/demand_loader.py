from __future__ import annotations

from pathlib import Path
import zipfile

import pandas as pd


def load_operational_demand(demand_dir: Path | str = Path("data/demand")) -> pd.DataFrame:
    """Load AEMO operational demand rows from ZIP files.

    Returns a DataFrame with columns: timestamp, region, demand.
    """
    demand_path = Path(demand_dir)
    if not demand_path.exists():
        raise FileNotFoundError(f"Demand directory not found: {demand_path}")

    frames: list[pd.DataFrame] = []
    files_processed = 0
    total_rows_loaded = 0

    for zip_path in sorted(demand_path.rglob("*.zip")):
        with zipfile.ZipFile(zip_path, "r") as zf:
            csv_names = [
                name
                for name in zf.namelist()
                if name.lower().endswith(".csv") and not name.endswith("/")
            ]
            if not csv_names:
                continue

            with zf.open(csv_names[0]) as csv_file:
                # Rows have mixed shapes (C/I/D), so parse with fixed columns.
                df = pd.read_csv(csv_file, header=None, names=range(10), engine="python")

        data_rows = df[df[0] == "D"].loc[:, [5, 4, 6]].copy()
        data_rows.columns = ["timestamp", "region", "demand"]
        frames.append(data_rows)

        files_processed += 1
        total_rows_loaded += len(data_rows)

    result = (
        pd.concat(frames, ignore_index=True)
        if frames
        else pd.DataFrame(columns=["timestamp", "region", "demand"])
    )

    if not result.empty:
        result["timestamp"] = pd.to_datetime(
            result["timestamp"], format="%Y/%m/%d %H:%M:%S", errors="coerce"
        )
        result["demand"] = pd.to_numeric(result["demand"], errors="coerce")

    print(f"number of files processed: {files_processed}")
    print(f"total rows loaded: {total_rows_loaded}")

    return result


if __name__ == "__main__":
    operational_demand = load_operational_demand()
    print(operational_demand.head())

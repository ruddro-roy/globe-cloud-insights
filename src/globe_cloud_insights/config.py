"""Project-wide configuration constants."""

from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

RAW_CSV_PATH = RAW_DIR / "globe_clouds_2022.csv"
CLEAN_PARQUET_PATH = PROCESSED_DIR / "globe_clouds_2022_clean.parquet"

# ── GLOBE API ────────────────────────────────────────────────────────────────
GLOBE_API_BASE = "https://api.globe.gov/search/v1/measurement/protocol/measureddate"
GLOBE_PROTOCOL = "sky_conditions"
GLOBE_START_DATE = "2022-01-15"
GLOBE_END_DATE = "2022-02-15"

# ── Cloud-type taxonomy (GLOBE protocol categories) ─────────────────────────
CLOUD_GENERA = [
    "Cirrus",
    "Cirrocumulus",
    "Cirrostratus",
    "Altocumulus",
    "Altostratus",
    "Nimbostratus",
    "Stratocumulus",
    "Stratus",
    "Cumulus",
    "Cumulonimbus",
]

SKY_CONDITIONS = [
    "Clear",
    "Few",
    "Isolated",
    "Scattered",
    "Broken",
    "Overcast",
    "Obscured",
]

# ── Data citation (official GLOBE wording) ───────────────────────────────────
DATA_CITATION = (
    "Global Learning and Observations to Benefit the Environment (GLOBE) Program, "
    "{access_date}, globe.gov"
)

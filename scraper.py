import requests
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

@dataclass
class IPO:
    name: str
    gmp_percent: float
    issue_price: float
    lot_size: int
    min_investment: float
    estimated_listing: float
    status: str

GMP_THRESHOLD = 40.0
IST = timezone(timedelta(hours=5, minutes=30))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://www.investorgain.com",
    "Referer": "https://www.investorgain.com/",
}


def _api_url() -> str:
    now = datetime.now(IST)
    month = now.month
    year = now.year
    # Indian financial year: April–March
    fy_start = year if month >= 4 else year - 1
    fy = f"{fy_start}-{str(fy_start + 1)[2:]}"
    return f"https://webnodejs.investorgain.com/cloud/v2/report/data-read/331/1/{month}/{year}/{fy}/0/all"


def get_filtered_ipos() -> list[IPO]:
    resp = requests.get(_api_url(), headers=HEADERS, timeout=15)
    resp.raise_for_status()
    rows = resp.json().get("reportTableData", [])

    ipos = []
    for row in rows:
        try:
            status = row.get("~ipo_status1", "")
            if status != "O":
                continue

            gmp_percent = float(row.get("~gmp_percent_calc", 0) or 0)
            if gmp_percent <= GMP_THRESHOLD:
                continue

            name = row.get("~ipo_name", "").strip() + " IPO"
            issue_price = float(str(row.get("Price (₹)", 0)).replace(",", "") or 0)
            lot_size = int(str(row.get("Lot", 0)).replace(",", "") or 0)
            if issue_price <= 0 or lot_size <= 0:
                continue

            estimated_listing = round(issue_price * (1 + gmp_percent / 100), 2)

            ipos.append(IPO(
                name=name,
                gmp_percent=gmp_percent,
                issue_price=issue_price,
                lot_size=lot_size,
                min_investment=round(issue_price * lot_size, 2),
                estimated_listing=estimated_listing,
                status="Open",
            ))
        except (ValueError, TypeError):
            continue

    return ipos

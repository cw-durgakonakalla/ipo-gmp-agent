import requests
from researcher import ResearchedIPO

MEDALS = ["1️⃣", "2️⃣", "3️⃣"]


def _esc(text: str) -> str:
    """Escape MarkdownV2 special characters."""
    for ch in r"\.+()!-=#|{}[]":
        text = text.replace(ch, f"\\{ch}")
    return text


def format_message(ipos: list[ResearchedIPO], run_time: str) -> str:
    lines = [
        f"📊 *IPO GMP Alert — {run_time} IST*",
        f"🏆 *TOP {len(ipos)} IPO\\(s\\) Worth Watching Today*",
        "",
    ]
    for i, ipo in enumerate(ipos):
        medal = MEDALS[i] if i < len(MEDALS) else f"{i+1}\\."
        lines += [
            f"{medal} *{_esc(ipo.name)}*",
            f"   GMP: \\+{_esc(str(ipo.gmp_percent))}% \\| Issue Price: ₹{_esc(str(ipo.issue_price))}",
            f"   💰 Min Investment: ₹{_esc(f'{ipo.min_investment:,.0f}')} \\({ipo.lot_size} shares × ₹{_esc(str(ipo.issue_price))}\\)",
        ]
        for point in ipo.strong_points:
            lines.append(f"   ✅ {_esc(point)}")
        for point in ipo.weak_points[:1]:
            lines.append(f"   ⚠️ {_esc(point)}")
        lines.append("")

    lines.append("⚡ _Powered by Gemini AI \\+ investorgain\\.com_")
    return "\n".join(lines)


def send_telegram(ipos: list[ResearchedIPO], run_time: str, bot_token: str, chat_id: str):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    response = requests.post(url, json={
        "chat_id": chat_id,
        "text": format_message(ipos, run_time),
        "parse_mode": "MarkdownV2",
    }, timeout=10)
    response.raise_for_status()


def send_heartbeat(run_time: str, bot_token: str, chat_id: str):
    text = (
        "📊 *IPO GMP Weekly Check — {time} IST*\n\n"
        "✅ Agent is alive and running\\.\n"
        "❌ No open IPOs with GMP ≥ 40% today\\.\n\n"
        "⚡ _Powered by Gemini AI \\+ investorgain\\.com_"
    ).format(time=run_time)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    response = requests.post(url, json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2",
    }, timeout=10)
    response.raise_for_status()

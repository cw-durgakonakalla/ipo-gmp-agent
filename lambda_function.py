import boto3
import logging
from datetime import datetime, timezone, timedelta

from scraper import get_filtered_ipos
from deduplicator import filter_already_sent, mark_as_sent
from researcher import research_ipos
from ranker import pick_top_3
from notifier import send_telegram, send_heartbeat

logger = logging.getLogger()
logger.setLevel(logging.INFO)

IST = timezone(timedelta(hours=5, minutes=30))
REGION = "ap-south-1"


def _get_secret(ssm_client, name: str) -> str:
    return ssm_client.get_parameter(Name=name, WithDecryption=True)["Parameter"]["Value"]


def _ist_now() -> datetime:
    return datetime.now(IST)


def _ist_time(now: datetime) -> str:
    return now.strftime("%I:%M %p").lstrip("0")


def handler(event, context):
    logger.info("IPO GMP Agent starting")

    now = datetime.now(IST)
    is_friday = now.weekday() == 4  # Monday=0, Friday=4

    ipos = get_filtered_ipos()
    logger.info(f"Open IPOs with GMP >= 40%%: {len(ipos)}")

    ssm = boto3.client("ssm", region_name=REGION)
    bot_token = _get_secret(ssm, "/ipo-agent/telegram-bot-token")
    chat_id   = _get_secret(ssm, "/ipo-agent/telegram-chat-id")
    run_time  = _ist_time(now)

    if not ipos:
        if is_friday:
            logger.info("Friday heartbeat: sending no-IPO message")
            send_heartbeat(run_time, bot_token, chat_id)
            return {"statusCode": 200, "body": "Friday heartbeat sent"}
        logger.info("No qualifying IPOs and not Friday — skipping alert")
        return {"statusCode": 200, "body": "No open IPOs above 40% GMP"}

    ipos = filter_already_sent(ipos)
    logger.info(f"After deduplication: {len(ipos)} new IPOs")
    if not ipos:
        return {"statusCode": 200, "body": "All qualifying IPOs already sent today"}

    gemini_key = _get_secret(ssm, "/ipo-agent/gemini-api-key")
    researched = research_ipos(ipos, gemini_key=gemini_key)
    top3 = pick_top_3(researched)

    send_telegram(top3, run_time, bot_token, chat_id)
    mark_as_sent(top3)

    logger.info(f"Alert sent for {len(top3)} IPOs")
    return {"statusCode": 200, "body": f"Sent alert for {len(top3)} IPOs"}

# IPO GMP Agent

An AWS Lambda function that watches Indian IPOs for high Grey Market Premium (GMP),
enriches the strongest candidates with Gemini AI analysis, and sends a daily alert to Telegram.

## How it works

1. **`scraper.py`** — pulls live IPO data from investorgain.com and keeps only IPOs
   that are currently open with GMP ≥ 40%.
2. **`deduplicator.py`** — filters out IPOs already alerted on today (state kept in
   SSM Parameter Store) so the same IPO isn't sent twice in one day.
3. **`researcher.py`** — asks Gemini for strong/weak points and a 1–10 score for each
   remaining IPO.
4. **`ranker.py`** — ranks by a blend of GMP % and AI score, keeping the top 3.
5. **`notifier.py`** — formats and sends the alert as a Telegram message.
6. **`lambda_function.py`** — the Lambda entry point (`handler`) that wires the steps
   above together. If no IPO qualifies, it stays silent on weekdays and sends a
   "still alive" heartbeat on Fridays.

## Configuration

Secrets are read from AWS Systems Manager Parameter Store (`ap-south-1`) at runtime,
not from environment variables or code:

| Parameter | Purpose |
|---|---|
| `/ipo-agent/telegram-bot-token` | Telegram bot token used to send alerts |
| `/ipo-agent/telegram-chat-id` | Telegram chat/channel to post to |
| `/ipo-agent/gemini-api-key` | Google Gemini API key for IPO research |
| `/ipo-agent/sent-today` | Internal — tracks which IPOs were already alerted today |

## Running locally

```bash
pip install -r requirements.txt
```

Then invoke `lambda_function.handler(event, context)` with valid AWS credentials
configured (the SSM parameters above must exist in your account).

## Deployment

Packaged and deployed as an AWS Lambda function (Python 3.12), triggered on a schedule
(e.g. EventBridge) to run once per day.

## Notes

- `check_site.py` is a scratch script used to explore investorgain.com's page structure
  while building the scraper — not part of the Lambda's runtime path.

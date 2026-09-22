import boto3
from botocore.exceptions import ClientError
from datetime import date

PARAM_NAME = "/ipo-agent/sent-today"
REGION = "ap-south-1"

_client = None


def _ssm():
    global _client
    if _client is None:
        _client = boto3.client("ssm", region_name=REGION)
    return _client


def ssm_get(name: str) -> str | None:
    try:
        return _ssm().get_parameter(Name=name)["Parameter"]["Value"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "ParameterNotFound":
            return None
        raise


def ssm_put(value: str):
    _ssm().put_parameter(Name=PARAM_NAME, Value=value, Type="String", Overwrite=True)


def filter_already_sent(ipos: list) -> list:
    """Accepts any list of objects with a .name attribute (IPO or ResearchedIPO)."""
    cache = ssm_get(PARAM_NAME)
    if not cache:
        return ipos
    today = date.today().isoformat()
    if not cache.startswith(today):
        return ipos  # Different day — treat cache as empty
    sent = set(cache.split(":")[1].split(",")) if ":" in cache else set()
    return [ipo for ipo in ipos if ipo.name not in sent]


def mark_as_sent(ipos: list):
    """Accepts any list of objects with a .name attribute (IPO or ResearchedIPO)."""
    today = date.today().isoformat()
    cache = ssm_get(PARAM_NAME)
    existing = []
    if cache and cache.startswith(today) and ":" in cache:
        existing = cache.split(":")[1].split(",")
    all_names = existing + [ipo.name for ipo in ipos]
    ssm_put(f"{today}:{','.join(all_names)}")

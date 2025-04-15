import datetime


def utc_now_aware() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def utc_now_naive() -> datetime.datetime:
    return utc_now_aware().astimezone(None)

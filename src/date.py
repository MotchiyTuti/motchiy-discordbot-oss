from datetime import date


def future(mm_dd: str) -> str:
    today = date.today()
    month, day = map(int, mm_dd.split("-"))
    target = date(today.year, month, day)
    if target <= today:
        target = date(today.year + 1, month, day)
    return target.strftime("%Y-%m-%d")


def past(mm_dd: str) -> str:
    today = date.today()
    month, day = map(int, mm_dd.split("-"))
    target = date(today.year, month, day)
    if target >= today:
        target = date(today.year - 1, month, day)
    return target.strftime("%Y-%m-%d")
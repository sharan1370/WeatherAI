from datetime import date, timedelta


def get_today() -> str:
    """
    Return today's date.
    """
    return date.today().isoformat()


def get_yesterday() -> str:
    """
    Return yesterday's date.
    """
    return (
        date.today() - timedelta(days=1)
    ).isoformat()
def get_date_days_ago(days: int) -> str:
    """
    Return a date a specified number of days ago.
    """

    return (
        date.today() - timedelta(days=days)
    ).isoformat()

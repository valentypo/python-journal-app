from datetime import date, timedelta

def build_journal_text(entries):
    text = ""
    for i, entry in enumerate(entries, start=1):
        text += f"""
        Entry {i}
        Title: {entry['title']}
        Content: {entry['content']}
        """
    return text


def get_date_range(period: str):
    today = date.today()

    if period == "daily":
        start = today
        end = today

    elif period == "weekly":
        start = today - timedelta(days=7)
        end = today

    elif period == "monthly":
        start = today.replace(day=1)
        end = today

    else:
        raise ValueError("Invalid period")

    return (
        f"{start.isoformat()}T00:00:00",
        f"{end.isoformat()}T23:59:59",
    )

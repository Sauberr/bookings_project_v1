from datetime import datetime, timedelta


def get_month_days(date: datetime = datetime.today()):
    counter = datetime(date.year, date.month, datetime.today().day, tzinfo=date.tzinfo)
    date_list = []
    for _ in range(365*2):
        date_list.append(
            {"date": counter.date(), "date_formatted": counter.strftime("%Y-%m-%d")}
        )
        counter += timedelta(days=1)
    return date_list


def format_number_thousand_separator(
    number: int,
    separator: str = " ",
):
    return f"{number:,}".replace(",", separator)

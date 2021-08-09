import datetime


def get_next_day(date):
    """
    Get next date, date format yyyy-MM-dd
    :param date:
    :return:
    """
    next_date = datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=1)
    return next_date.strftime('%Y-%m-%d')
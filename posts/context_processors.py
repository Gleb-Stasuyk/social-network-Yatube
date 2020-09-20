import datetime as dt


def year(request):
    date = dt.datetime.today()
    year = date.year
    """
    Добавляет переменную с текущим годом.
    """
    return {
        'year': year,
    }

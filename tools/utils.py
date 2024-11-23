from datetime import datetime



def get_day_of_week(date: str) -> str:
    """
    Returns the day of the week for a given date
    """
    date = datetime.strptime(date, '%d/%m/%Y')
    return date.strftime('%A')








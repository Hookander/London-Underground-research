from datetime import datetime
from datetime import timedelta
from typing import List

def get_day_of_week(date: str) -> str:
    """
    Returns the day of the week for a given date
    """
    date = datetime.strptime(date, '%d/%m/%Y')
    return date.strftime('%A')

def get_type_of_day(day_of_week: str, include_friday = False) -> str:
    """
    Returns the type of day for a given day of the week
    """
    match day_of_week:
        case 'Monday' | 'Tuesday' | 'Wednesday' | 'Thursday':
            return 'MTT'
        case 'Friday':
            if include_friday:
                return 'FRI'
            return 'MTT'
        case 'Saturday':
            return 'SAT'
        case 'Sunday':
            return 'SUN'
        case _:
            raise ValueError('Invalid day of the week')

def reverser_direction(direction: str) -> str:
    """
    Returns the opposite direction
    """
    if direction == 'EB':
        return 'WB'
    elif direction == 'WB':
        return 'EB'
    raise ValueError('Invalid direction')

def get_destinations_ids_from_direction(direction: str) -> str:
    """
    Returns the destination from the direction
    """
    if direction == 'EB':
        return ('940GZZLUHLT', '940GZZLUEPG')
    elif direction == 'WB':
        return ('940GZZLUWRP', '940GZZLUEBY')
    raise ValueError('Invalid direction')

def get_dates_between(start_date: str, end_date: str) -> List[str]:
    """
    Returns a list of dates between the start and end date
    start_date = 'dd/mm'
    end_date = 'dd/mm'
    """
    start_date = datetime.strptime(start_date, '%d/%m/%Y')
    end_date = datetime.strptime(end_date, '%d/%m/%Y')
    dates = []
    while start_date <= end_date:
        dates.append(start_date.strftime('%d/%m/%Y'))
        start_date += timedelta(days=1)
    return dates

def nb_days_per_tod(year:str) -> int:
    """
    Returns the number of days for a given type of day and year
    """
    dates = get_dates_between('01/01/'+year, '31/12/'+year)
    count = {'MTT': 0, 'SAT': 0, 'SUN': 0, 'FRI': 0}
    for date in dates:
        count[get_type_of_day(get_day_of_week(date), include_friday=True)] += 1
    return count
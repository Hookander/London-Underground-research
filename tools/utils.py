from datetime import datetime



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





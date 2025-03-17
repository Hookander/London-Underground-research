from datetime import datetime
from datetime import timedelta
from typing import List
from math import radians, sin, cos, sqrt, atan2

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

def get_all_stations():
    return ['West Ruislip', 'Ruislip Gardens', 'South Ruislip', 'Northolt', 'Greenford',
            'Perivale', 'Hanger Lane', 'Ealing Broadway', 'West Acton', 'North Acton',
            'East Acton', 'White City', 'Shepherds Bush', 'Holland Park',
            'Notting Hill Gate', 'Queensway', 'Lancaster Gate', 'Marble Arch',
            'Bond Street', 'Oxford Circus', 'Tottenham Court Road', 'Holborn',
            'Chancery Lane', 'St Pauls', 'Bank', 'Liverpool Street', 'Bethnal Green',
            'Mile End', 'Stratford', 'Leyton', 'Leytonstone', 'Snaresbrook',
            'South Woodford', 'Woodford', 'Buckhurst Hill', 'Loughton', 'Debden',
            'Theydon Bois', 'Wanstead', 'Redbridge', 'Gants Hill', 'Newbury Park',
            'Barkingside', 'Fairlop', 'Hainault', 'Grange Hill', 'Chigwell',
            'Roding Valley', 'Epping']

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

def get_next_date(date: str) -> str:
    """
    Returns the next date
    """
    date = datetime.strptime(date, '%d/%m/%Y')
    date += timedelta(days=1)
    return date.strftime('%d/%m/%Y')

def station_coordinates(station):
    """
    Returns the coordinates of a station
    """
    central_line_stations = {
    "West Ruislip": (51.5696, -0.4371),
    "Ruislip Gardens": (51.5608, -0.4104),
    "South Ruislip": (51.5569, -0.3988),
    "Northolt": (51.5483, -0.3687),
    "Greenford": (51.5423, -0.3458),
    "Perivale": (51.5367, -0.3232),
    "Hanger Lane": (51.5302, -0.2933),
    "Ealing Broadway": (51.5152, -0.3015),
    "West Acton": (51.5179, -0.2807),
    "North Acton": (51.5237, -0.2597),
    "East Acton": (51.5173, -0.2479),
    "White City": (51.5121, -0.2240),
    "Shepherds Bush": (51.5048, -0.2187),
    "Holland Park": (51.5072, -0.2063),
    "Notting Hill Gate": (51.5087, -0.1965),
    "Queensway": (51.5105, -0.1877),
    "Lancaster Gate": (51.5119, -0.1758),
    "Marble Arch": (51.5136, -0.1586),
    "Bond Street": (51.5142, -0.1494),
    "Oxford Circus": (51.5152, -0.1415),
    "Tottenham Court Road": (51.5165, -0.1310),
    "Holborn": (51.5174, -0.1201),
    "Chancery Lane": (51.5183, -0.1111),
    "St Pauls": (51.5146, -0.0973),
    "Bank": (51.5133, -0.0886),
    "Liverpool Street": (51.5178, -0.0823),
    "Bethnal Green": (51.5270, -0.0549),
    "Mile End": (51.5253, -0.0332),
    "Stratford": (51.5417, -0.0037),
    "Leyton": (51.5566, -0.0054),
    "Leytonstone": (51.5683, 0.0083),
    "Snaresbrook": (51.5803, 0.0216),
    "South Woodford": (51.5914, 0.0275),
    "Woodford": (51.6065, 0.0341),
    "Buckhurst Hill": (51.6266, 0.0471),
    "Loughton": (51.6415, 0.0558),
    "Debden": (51.6453, 0.0838),
    "Theydon Bois": (51.6717, 0.1032),
    "Wanstead": (51.5755, 0.0288),
    "Redbridge": (51.5763, 0.0454),
    "Gants Hill": (51.5765, 0.0663),
    "Newbury Park": (51.5756, 0.0899),
    "Barkingside": (51.5851, 0.0889),
    "Fairlop": (51.5955, 0.0912),
    "Hainault": (51.6030, 0.0934),
    "Grange Hill": (51.6132, 0.0925),
    "Chigwell": (51.6180, 0.0745),
    "Roding Valley": (51.6171, 0.0445),
    "Epping": (51.6937, 0.1139)}
    return central_line_stations[station]

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points 
    on the Earth (in kilometers)
    """
    R = 6371  # Earth radius in kilometers
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    a = (sin(dLat/2) * sin(dLat/2) +
         cos(radians(lat1)) * cos(radians(lat2)) *
         sin(dLon/2) * sin(dLon/2))
    return R * 2 * atan2(sqrt(a), sqrt(1-a))
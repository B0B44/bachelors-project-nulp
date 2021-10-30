from math import cos, radians, sin, sqrt, atan2


def distance_between_latlng(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculates distance between two sets of latitude and longitude.
    Returns distance in kilometers.

    Reference: my personal ingress fielding project.

    :param lat1:
    :param lng1:
    :param lat2:
    :param lng2:
    :return:
    """
    radius = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lng1)
    lat2 = radians(lat2)
    lon2 = radians(lng2)

    d_lon = lon2 - lon1
    d_lat = lat2 - lat1

    a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    dist = radius * c
    return dist

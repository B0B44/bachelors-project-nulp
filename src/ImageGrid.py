from math import cos, pi
from typing import Tuple, Dict

from utils.distance_between_latlng import distance_between_latlng

from tqdm import tqdm
from src.SatelliteImage import SatelliteImage
from shapely.geometry import Point
from osmnx.geocoder import geocode_to_gdf


class ImageGrid:
    """
    This class is responsible for generating 2d array (grid) of latlngs around the center coordinate
    """
    scale = 0.190  # km per 512 px

    def __init__(self, country: str, city: str, central_latitude: float, central_longitude: float, radius: float = 10):
        # km per 512 px
        scale_vertical = self.scale
        scale_horizontal = self.scale
        # in case of a globe-like map we would use use following formula for spacing
        # scale_horizontal = self.scale * abs(cos(latitude * pi / 180))

        # km / km per 512 px = num of 512 px
        swing_vertical = int(radius / 2 // scale_vertical)
        swing_horizontal = int(radius / 2 // scale_horizontal)

        # km per 512 px
        offset_vertical = self.scale / 110
        offset_horizontal = self.scale / 110 / abs(cos(central_latitude * pi / 180))

        self.grid: Dict[Tuple[int, int], SatelliteImage] = dict()

        try:
            geom = geocode_to_gdf({'city': city, 'country': country}).loc[0, 'geometry']
        except ValueError:
            geom = geocode_to_gdf({'city': city}).loc[0, 'geometry']

        for i in range(-swing_vertical, swing_vertical + 1):
            for j in range(-swing_horizontal, swing_horizontal + 1):
                lat = round(central_latitude + (2 * i * offset_vertical), 6)
                lng = round(central_longitude + (2 * j * offset_horizontal), 6)
                if distance_between_latlng(central_latitude, central_longitude, lat, lng) <= radius and \
                        geom.intersects(Point(lng, lat)):
                    self.grid[i, j] = SatelliteImage(lat, lng)

    def save_all(self):
        for value in tqdm(self.grid.values()):
            value.save_if_not_exist()

    def print_to_intel(self):
        result = []
        for value in self.grid.values():
            result.append('{"type":"marker","latLng":{'
                          + f'"lat":{value.latitude},"lng":{value.longitude}'
                          + '},"color":"#a24ac3"}')
        print('[' + ','.join(result) + ']')

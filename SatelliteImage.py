import io
import os
from typing import Optional

import np as np
import requests as requests
import matplotlib.pyplot as plt
import matplotlib.image as mpl_img

from FileHandler import FileHandler

if os.environ.get('MAPS_API_KEY_NULP') is None:
    import getpass
    os.environ['MAPS_API_KEY_NULP'] = getpass.getpass('Please enter your api key')


class SatelliteImage:
    zoom = 17
    data_path = 'raw_data'
    KEY = os.environ.get('MAPS_API_KEY_NULP')

    def __init__(self, latitude: float, longitude: float, lazy_load=True):
        self.latitude: float = latitude
        self.longitude: float = longitude
        self.__image: Optional[np.ndarray] = None

        if not lazy_load:
            self.load()

    @property
    def image(self) -> np.ndarray:
        if self.__image is None:
            self.load()
        return self.__image

    def pull_image(self) -> bytes:
        base_url = 'https://maps.googleapis.com/maps/api/staticmap?'

        center = f'{self.latitude},{self.longitude}'
        zoom = str(self.zoom)
        scale = '2'  # 'false' or '2'
        size = '640x640'  # max size
        maptype = 'satellite'  # 'roadmap', 'terrain', 'satellite', or 'hybrid'
        _format = 'png'  # 'png', 'gif' ,'jpg'

        params = [f'center={center}',
                  f'zoom={zoom}',
                  f'scale={scale}',
                  f'size={size}',
                  f'maptype={maptype}',
                  f'key={self.KEY}',
                  f'format={_format}',
                  f'visual_refresh=true']

        url = base_url + '&'.join(params)

        # No need to double quote
        # url = requests.utils.quote(url)

        print('Sending network request')
        response = requests.get(url)

        assert response.status_code == 200,\
            f'Something went wrong with the request, request status code: {response.status_code}'

        return response.content

    @staticmethod
    def decode_image(data: bytes) -> np.ndarray:
        with io.BytesIO(data) as source:
            return mpl_img.imread(source, format='png')

    @staticmethod
    def encode_image(image: np.ndarray) -> bytes:
        with io.BytesIO() as output:
            mpl_img.imsave(output, image, format='png')
            return output.getvalue()

    def save(self):
        data: bytes = self.encode_image(self.image)

        FileHandler.image_save(self.latitude, self.longitude, data)

    def load(self):
        if FileHandler.image_exists(self.latitude, self.longitude):
            data = FileHandler.image_load(self.latitude, self.longitude)
        else:
            data = self.pull_image()

        self.__image = self.decode_image(data)

    def display(self):
        plt.imshow(self.image)
        plt.show()


if __name__ == '__main__':
    ...

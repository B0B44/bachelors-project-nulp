import atexit
import os

import requests

if os.environ.get('MAPS_API_KEY_NULP') is None:
    import getpass
    os.environ['MAPS_API_KEY_NULP'] = getpass.getpass('Please enter your api key')


class API:
    """
    This class is responsible for api communication and without actually knowing anything about the data.
    That is delegated to image class.
    """
    KEY = os.environ.get('MAPS_API_KEY_NULP')
    try:
        with open('request_count_left.int') as file:
            request_count_left = int(file.read())
    except FileNotFoundError:
        request_count_left = 0
    zoom = '17'
    scale = '2'  # 'false' or '2'
    size = '640x640'  # max size
    maptype = 'satellite'  # 'roadmap', 'terrain', 'satellite', or 'hybrid'
    format = 'png'  # 'png', 'gif' ,'jpg'
    visual_refresh = 'true'

    @classmethod
    def save_counter(cls):
        print('Saving requests count to file')
        with open('request_count_left.int', 'w') as file:
            file.write(f'{cls.request_count_left}')

    @classmethod
    def pull(cls, lat, lng):
        base_url = 'https://maps.googleapis.com/maps/api/staticmap?'

        params = [f'center={lat},{lng}',
                  f'zoom={cls.zoom}',
                  f'scale={cls.scale}',
                  f'size={cls.size}',
                  f'maptype={cls.maptype}',
                  f'key={cls.KEY}',
                  f'format={cls.format}',
                  f'visual_refresh={cls.visual_refresh}']

        url = base_url + '&'.join(params)

        response = requests.get(url)

        assert response.status_code == 200, \
            f'Something went wrong with the request, request status code: {response.status_code}'

        return response.content


@atexit.register
def _save_count():
    API.save_counter()

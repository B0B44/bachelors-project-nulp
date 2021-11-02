import atexit
import os
import urllib.parse as urlparse
import hashlib
import hmac
import base64

import requests

if os.environ.get('MAPS_API_KEY_NULP') is None:
    import getpass
    os.environ['MAPS_API_KEY_NULP'] = getpass.getpass('Please enter your api key')

if os.environ.get('MAPS_API_SECRET_NULP') is None:
    import getpass
    os.environ['MAPS_API_SECRET_NULP'] = getpass.getpass('Please enter your api key')


class API:
    """
    This class is responsible for api communication and without actually knowing anything about the data.
    That is delegated to image class.
    """
    KEY = os.environ.get('MAPS_API_KEY_NULP')
    SECRET = os.environ.get('MAPS_API_SECRET_NULP')
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
        if cls.request_count_left <= 0:
            print('No more requests quota left')
            exit(1)
            raise IOError('No more requests quota left')

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

        url = cls.sign_url(url)

        response = requests.get(url)
        cls.request_count_left -= 1

        assert response.status_code == 200, \
            f'Something went wrong with the request, request status code: {response.status_code}'

        return response.content

    @classmethod
    def sign_url(cls, input_url: str) -> str:
        """
        This method sings the url with the digital signature as it is needed in case of 25k + requests per day
        Also security, bla bla bla

        :param input_url:
            Unsigned url
        :return:
            Signed url
        """
        url = urlparse.urlparse(input_url)

        # We only need to sign the path+query part of the string
        url_to_sign = url.path + "?" + url.query

        # Decode the private key into its binary format
        # We need to decode the URL-encoded private key
        decoded_key = base64.urlsafe_b64decode(cls.SECRET)

        # Create a signature using the private key and the URL-encoded
        # string using HMAC SHA1. This signature will be binary.
        signature = hmac.new(decoded_key, str.encode(url_to_sign), hashlib.sha1)

        # Encode the binary signature into base64 for use within a URL
        encoded_signature = base64.urlsafe_b64encode(signature.digest())

        original_url = url.scheme + "://" + url.netloc + url.path + "?" + url.query

        # Return signed URL
        return original_url + "&signature=" + encoded_signature.decode()


@atexit.register
def _save_count():
    API.save_counter()

import io
from typing import Optional

import np as np
import matplotlib.pyplot as plt
import matplotlib.image as mpl_img

from src.FileHandler import FileHandler
from src.API import API


class SatelliteImage:
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
            data = API.pull(self.latitude, self.longitude)
        self.__image = self.decode_image(data)

    def display(self):
        plt.imshow(self.image)
        plt.show()


if __name__ == '__main__':
    ...

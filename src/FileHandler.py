import atexit
import pickle
from pathlib import Path

from typing import Dict, Optional, Set


class FileHandler:
    """
    This class is responsible for program interaction with saved images,
     it keeps index of images for faster image lookup
    """
    file_format: str = '.png'
    data_dir: Path = Path('data')
    index_path: Path = Path('index.pickle')
    full_index_path: Optional[Path] = None
    index: Dict[int, Set[str]] = {0: {'0'}}  # need to add dummy key & value for pickle

    @classmethod
    def initialize(cls) -> None:
        """
        This method should be called before any usage of class.
        It ensures that necessary folders actually exists, and the class will work correctly.

        :return: None
        """
        cls.data_dir.mkdir(exist_ok=True)
        cls.full_index_path = cls.data_dir.joinpath(cls.index_path)

        if not cls.full_index_path.exists():
            cls.full_index_path.touch()
            cls.index_save()

        cls.index_load()
        atexit.register(cls.index_save)

    @classmethod
    def index_load(cls) -> None:
        print('Saving file index to file')
        with open(cls.full_index_path, 'rb') as file:
            cls.index = pickle.load(file)

    @classmethod
    def index_save(cls) -> None:
        with open(cls.full_index_path, 'wb') as file:
            pickle.dump(cls.index, file)

    @classmethod
    def index_add(cls, lat: float, lng: float, filepath: str) -> None:
        key = cls.get_keys(lat, lng)

        if key not in cls.index:
            cls.index[key] = set()

        cls.index[key].add(filepath)

    @classmethod
    def index_rescan(cls) -> None:
        # todo
        ...

    @classmethod
    def get_keys(cls, lat: float, lng: float) -> int:
        """
        Generating single int key from lat & lng for quick & easy hashing

        For example:
        lat = -42.5923
        lng = 150.6814

        The resulting key will be
         4259 # lat part
          15068 # lng part
        key = 425915068

        Result should ensure that group size for one key is no more then 1.1 km * 1.1 km * 4 (cells on a globe)
        Reference: https://en.wikipedia.org/wiki/Decimal_degrees

        :param lat: float
        :param lng: float
        :return: int
            Key
        """
        key = abs(round(lat * 100)) * 100_000
        key = abs(round(lng * 100)) + key
        return key

    @classmethod
    def image_get_full_path(cls, lat: float, lng: float, create: bool = True) -> Path:
        """
        This function will use weird mix of decimal degrees and DMS notation, in order to avoid using negative signs
        in the filename

        :param lat:
        :param lng:
        :param create: bool, optional
            Tells the function whether to create the folder if one does not exist
        :return: Path
            Returns the full path to where the file should be stored
        """
        first_part = f'{abs(lat):.06f}°{"N" if lat > 0 else "S"}'.replace('.', '_')
        second_part = f'{abs(lng):.06f}°{"E" if lat > 0 else "W"}'.replace('.', '_')
        filename = Path(f'{first_part} {second_part}').with_suffix(cls.file_format)

        dir_path = cls.data_dir.joinpath(
            f'{round(lat)}',
            f'{round(lng)}',
        )

        if create:
            dir_path.mkdir(exist_ok=True, parents=True)

        full_path = dir_path.joinpath(filename)

        return full_path

    @classmethod
    def image_save(cls, lat: float, lng: float, data: bytes) -> None:
        full_path = cls.image_get_full_path(lat, lng)
        with open(full_path, 'wb') as file:
            file.write(data)
        cls.index_add(lat, lng, full_path.as_posix())

    @classmethod
    def image_load(cls, lat: float, lng: float) -> bytes:
        with open(cls.image_get_full_path(lat, lng), 'rb') as file:
            return file.read()

    @classmethod
    def image_exists(cls, lat: float, lng: float) -> bool:
        full_path = cls.image_get_full_path(lat, lng, create=False)
        key = cls.get_keys(lat, lng)
        if key in cls.index:
            if full_path.as_posix() in cls.index[key]:
                return True
        return False


FileHandler.initialize()

if __name__ == '__main__':
    ...

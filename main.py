import time

import pandas as pd

from src.ImageGrid import ImageGrid

if __name__ == '__main__':
    cities = pd.read_csv('worldcities.csv')

    countries = ['Austria', 'Belgium', 'Czechia', 'Denmark', 'France', 'Germany', 'Hungary', 'Luxembourg',
                 'Netherlands', 'Poland', 'Romania', 'Slovakia', 'Slovenia']
    selection = cities.loc[(cities.country.isin(countries)) & (cities.population >= 100000)]

    for row in selection.itertuples():
        try:
            grid = ImageGrid(row.country, row.city_ascii, row.lat, row.lng)
            print(f'Saving city {row.city}')
            time.sleep(0.1)
            grid.save_all()
        except ValueError:
            # todo move exception handling where it belongs (to ImageGrid)
            print(f'ValueError raised for {row.country}, {row.city}')

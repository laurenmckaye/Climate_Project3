import pandas as pd
import os

def load_city_climate_data(city_folder):
    
    city_data = []
    for filename in os.listdir(city_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(city_folder, filename)
        
            df = pd.read_csv(file_path)
            year = filename[-8:-4]
            df = df[['DATE', 'HourlyWindSpeed']]
            df['Station'] = city_folder.capitalize()
            df['Year'] = year
            city_data.append(df)
    return pd.concat(city_data, ignore_index=True)


def load_data(city_folders):
    return pd.concat([load_city_climate_data(f) for f in city_folders], ignore_index=True)
# import folium package and create map
import os
import folium
import requests
from dotenv import load_dotenv
from flask import render_template

load_dotenv()


def get_current_geomap(latitude, longtitude, city):

    request_url = (f'https://api.openweathermap.org/data/2.5/weather?appid={os.getenv("API_KEY")}&q={city}&lang=bg'
                   f'&units=metric')
    weather_data_coord = requests.get(request_url).json().get('coord')['lat'], requests.get(request_url).json().get('coord')['lon']

    print(weather_data_coord)

    latitude = weather_data_coord[0]
    longitude = weather_data_coord[1]


    generated_map = folium.Map(location=[latitude, longitude], zoom_start=12)

    # Pass a string in popup parameter
    folium.Marker([latitude, longitude], popup='Just search for "https://predictorian.online"').add_to(generated_map)

    generated_map.save("templates/generated_map.html")

    templates

    return generated_map, render_template("geo_map.html")

Simple Flask Web App to keep you informed to weather in cities of your choice worldwide that you like to check out the weather,wind speed and etc.

## How to use
Start the server with "python server.py" open the browser and navigate to http://127.0.0.1:8000 or corresponding port it is the number after the ":" in the URL.

Just type in your city name in the search bar and you will get the weather details of that city.

Be sure to check out the supported_languages.txt file for the list of supported languages and matching codes.Language can be changed in the weather.py file in particular in the get_current_weather() function in the API call (&lang=bg&units=metric).Units can be three types of metric(Celsius),imperial(Fahrenheit) or standard(Kalvin).In this example we have used metric units and Bulgarian(bg) language. You can adjust it accordingly.
Simple Flask Web App to keep you informed to weather in cities of your choice worldwide that you like to check out the weather,wind speed etc.

## How to use
Start the server with "python server.py" open the browser and navigate to http://127.0.0.1:8000 or corresponding port it is the number after the ":" in the URL.

Just type in your city name in the search bar, and you will get the weather details of that city.

Be sure to check out the supported_languages.txt file for the list of supported languages and matching codes.Language can be changed in the weather.py file in particular in the get_current_weather() function in the API call (&lang=bg&units=metric).Units can be three types of metric(Celsius),imperial(Fahrenheit) or standard(Kalvin).In this example we have used metric units and Bulgarian(bg) language. You can adjust it accordingly.

###
Important to do first!!!
###

1. sudo apt install gcc g++ cmake cmake-doc ccache

2. sudo apt install build-essential python3-dev python3-pip python3-venv libpcre3-dev

3. in shell (bash) use python3 -m venv .venv to create virtual environment after you changed 
to root directory of the project e.g. /home/$USER/python-check-weather 

4. source .venv/bin/activate to activate your environment 

e.g .venv here is for your virtual environment on your project whatever you named it
and with source in fact you're activating it.
Afterward since it's activated you can install the requirements and dependencies with pip 
and last step is to [install uwsgi with pip also (IMPORTANT) e.g. pip install uwsgi].
If the steps are successfully completed in that order you`re closing the final

You`ll need to properly configure the nginx web server using the example file given for 
virtual server block

after that you`ll got access to the website but with no ssl/tls encryption you can choose
from a plenty free and paid Certificate Authorities or Issuers or you can use ACME services which are free with much info and support 
on that task [also supports wildcards (*.example.com)] 

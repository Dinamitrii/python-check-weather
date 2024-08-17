Simple Flask Web App to keep you informed to weather in cities of your choice worldwide that you like to check out the weather,wind speed etc.

## How to use
Start the server with "python server.py" open the browser and navigate to http://127.0.0.1:8000 or corresponding port it is the number after the ":" in the URL.

Just type in your city name in the search bar, and you will get the weather details of that city.

Be sure to check out the supported_languages.txt file for the list of supported languages and matching codes.Language can be changed in the weather.py file in particular in the get_current_weather() function in the API call (&lang=bg&units=metric).Units can be three types of metric(Celsius),imperial(Fahrenheit) or standard(Kalvin).In this example we have used metric units and Bulgarian(bg) language. You can adjust it accordingly.

###
Important to do first!!!
###
1.
sudo apt install gcc g++ cmake cmake-doc ccache
sudo apt install build-essential python3-dev python3-pip libpcre3-dev
2.
cd to/project/directory/
3.
source .venv/bin/activate

in e.g .venv here is for your virtual environment on your project whatever you named it
and with source in fact you`re activating it.
Afterwards since it`s activated you can install the requirements and dependencies with pip 
and last step is to install uwsgi with pip also 
e.g pip install uwsgi
If the steps are successfully completed in that order you`re closing the final

You`ll need to proper configure the nginx web server using the example .txt file given for virtual server block

after that you`ll got access to the website but with no ssl/tls encryption you can choose
from a plenty free and paid Certificate Authorities or Issuers or you can use ACME services which are free with much info and support 
on that task [also supports wildcards (*.example.com) ] 

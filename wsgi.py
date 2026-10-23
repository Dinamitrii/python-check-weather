from server import app
from waitress import serve
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')


if __name__ == "__main__":
    serve(app.run(host="0.0.0.0", port=8000))

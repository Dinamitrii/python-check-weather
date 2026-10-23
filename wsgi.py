from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")  # before importing server

from server import app  # noqa: E402  (uWSGI uses wsgi:app)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8000)

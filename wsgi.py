from pathlib import Path

from dotenv import load_dotenv

# Load .env next to this file regardless of the working directory (before importing server)
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

from server import app  # noqa: E402,F401  (uWSGI/waitress use wsgi:app)

if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=8000)

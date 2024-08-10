from server import app
from waitress import serve

if __name__ == "__main__":
    serve(app.run(host="0.0.0.0", port=8000))

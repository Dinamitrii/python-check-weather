from flask import Flask, render_template
from waitress import serve

app = Flask(__name__)


@app.route("/")
@app.route("/index/")
def index():
    return render_template("index.html")


@app.route("/contacts/")
def contacts():
    return render_template("contacts.html")


if __name__ == "__main__":
    serve(app.run(host="0.0.0.0", port=8000))

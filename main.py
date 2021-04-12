from flask import Flask, redirect, url_for
from init import getProperties




app = Flask(__name__)


@app.route("/")
def login():
    return "Labas"

@app.route("/callback")
def callback():
    return "Labas"

if __name__ == '__main__':
    app.run(port=4996)


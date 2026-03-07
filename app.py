# Flask app
from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/hello')
def hello_name():
    name=request.args.get("name","Flask")
    return f"Hello, {escape(name)}!"
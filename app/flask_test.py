from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "<h1>Flask is Working!</h1><p>We can proceed with the conversion.</p>"

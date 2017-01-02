import os

from flask import Flask
from flask_sslify import SSLify

app = Flask(__name__)
sslify = SSLify(app)
config_path = os.environ.get("CONFIG_PATH", "crossword.config.DevelopmentConfig")
app.config.from_object(config_path)

from . import views
from . import filters
from . import login


    
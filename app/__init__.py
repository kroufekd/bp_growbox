from flask import Flask

app = Flask(__name__)

from .camera import camera
from .fan_control import fan
from .database import db
from .routes import *

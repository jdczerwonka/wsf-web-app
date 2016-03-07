"""
The flask application package.
"""

from flask import Flask
from flask_restful import Api
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/api/*" : {"origins" : "*" }})

import FlaskWebProject.views

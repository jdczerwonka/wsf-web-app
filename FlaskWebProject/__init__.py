"""
The flask application package.
"""

from flask import Flask
from flask_restful import Api
app = Flask(__name__)
api = Api(app)

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    'todo3': {'task': 'profit!'},
}

import FlaskWebProject.views

"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from FlaskWebProject.db.resources import *
from FlaskWebProject import app, api

API_HEADER = '/api/v1'

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/weightOpt')
def weightOpt():
    """Renders the Weight Optimization page."""
    return render_template(
        'weightOpt.html',
        title='Weight Optimization',
        year=datetime.now().year,
        message='Determine the optimal selling weight for a group of pigs.'
    )

api.add_resource(IngredientsApi, API_HEADER + '/ingredients', API_HEADER + '/ingredients/<IngrStr>')
api.add_resource(GroupsApi, API_HEADER + '/groups', API_HEADER + '/groups/<GroupStr>', API_HEADER + '/groups/<GroupStr>/<GroupInfo>')
api.add_resource(WeightOptApi, API_HEADER + '/weightOptApi')
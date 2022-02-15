from flaskr.__init__ import create_app

import os
import configparser
from flask_cors import CORS, cross_origin


config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join("config.ini")))


app = create_app()
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['DEBUG'] = True
app.config['MONGO_URI'] = config['TEST']['DB_URI']
app.run()
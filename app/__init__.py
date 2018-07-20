import config
from flask import Flask

app = Flask(__name__,static_url_path='')
app.config.from_mapping(
  SECRET_KEY = 'dev',
  SQLALCHEMY_DATABASE_URI = config.DBURI
)
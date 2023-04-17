from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis

# Create SQLAlchemy instance
db = SQLAlchemy()

# Create Redis instance
redis = FlaskRedis()
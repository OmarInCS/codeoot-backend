import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "codeoot.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

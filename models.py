from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
db = SQLAlchemy(app)


class Game(db.Model):
    __tablename__ = "games"

    game_datetime = db.Column(db.DateTime, primary_key=True)
    game_name = db.Column(db.String, nullable=False)
    duration = db.Column(db.String)
    start_datetime = db.Column(db.DateTime)
    players = db.relationship("Player", backref=db.backref("game"))
    game_pin = db.Column(db.String, nullable=False)


class Player(db.Model):
    __tablename__ = "players"

    player_id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String, nullable=False)
    game_datetime = db.Column(db.DateTime, db.ForeignKey("games.game_datetime"), nullable=False)
    submit_time = db.Column(db.DateTime)
    player_code = db.Column(db.String)

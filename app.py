from datetime import datetime, timedelta
import sys
import zlib
import config
from models import *
from flask_cors import CORS
from flask import (
    Flask,
    render_template,
    request, Response,
    flash,
    redirect,
    url_for,
    jsonify,
    abort
)

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app.config.from_object(config)
db.init_app(app)
db.create_all()

CORS(app, resources={r"/*": {"origins": "*"}})


'''
@TODO: Use the after_request decorator to set Access-Control-Allow
'''
# CORS Headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'application/json,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,PATCH')
    response.headers.add('Access-Control-Allow-Origin', 'https://codeoot-frontend.herokuapp.com')
    return response

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return jsonify({
        "message": "Welcome",
        "name": "Omar",
    })


@app.route('/games', methods=['POST'])
def create_game():
    """

    :return:
    """

    try:
        data = request.get_json()
        print(data)
        data["game_datetime"] = datetime.now()
        data["game_pin"] = str(int(data["game_datetime"].timestamp()))[-7:]
        game = Game(**data)
        db.session.add(game)
        db.session.commit()

    except:
        db.session.rollback()
        # flash('An error occurred. Show could not be listed.')
        print(sys.exc_info())
    else:
        # flash('Show was successfully listed!')
        return jsonify({
            "success": True,
            "game_pin": game.game_pin,
            "game_datetime": game.game_datetime.isoformat(" ", "seconds"),
        })
    finally:
        db.session.close()

    return jsonify({
        "success": False
    })


@app.route('/games/<game_datetime>', methods=['PATCH'])
def start_game(game_datetime: str):
    """
    :arg
    :returns
    """
    try:
        games = Game.query.all()
        game = list(filter(lambda game: game.game_datetime.isoformat(" ", "seconds") == game_datetime, games))[-1]
        print("-" * 20)
        if not game: abort(404)

        game.start_datetime = datetime.now()
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        return jsonify({
            "success": False
        })
    else:
        return jsonify({
            "success": True,
            "start_time": game.start_datetime.isoformat(" ", "seconds")
        })
    finally:
        db.session.close()


# TODO: add end point to update number of coders regularly

@app.route('/players/<game_datetime>', methods=['GET'])
def get_players_of_game(game_datetime: str):
    """
    :arg
    :returns
    """
    try:
        games = Game.query.all()
        game = list(filter(lambda game: game.game_datetime.isoformat(" ", "seconds") == game_datetime, games))[-1]
        players = Player.query.order_by(Player.submit_time.asc()).all()
        players = list(filter(lambda player: player.game_datetime.isoformat(" ", "seconds") == game_datetime, players))[:3]

        if len(players) == 0 or not game: abort(404)

        pt = datetime.strptime(game.duration,'%M:%S')
        game_time = timedelta(minutes=pt.minute, seconds=pt.second).total_seconds()

        response = [{
            "id": player.player_id,
            "name": player.player_name,
            "score": round((game_time - (player.submit_time - game.start_datetime).total_seconds()) * 5)
        } for player in players]

        return jsonify(response)
    except:
        db.session.rollback()
        print(sys.exc_info())
        return jsonify({
            "success": False
        })
    finally:
        db.session.close()


@app.route('/players', methods=['POST'])
def create_player():
    """

    :return:
    """

    try:
        print("-" * 20)
        data = request.get_json()
        print("-" * 20)
        game = Game\
            .query\
            .filter(Game.game_pin == data["game_pin"])\
            .order_by(Game.game_datetime.desc())\
            .first()

        if not game: abort(404)

        player = Player(
            player_name=data["player_name"],
            game_datetime=game.game_datetime
        )
        print("-" * 20)
        db.session.add(player)
        db.session.commit()

    except:
        db.session.rollback()
        # flash('An error occurred. Show could not be listed.')
        print(sys.exc_info())
    else:
        # flash('Show was successfully listed!')
        return jsonify({
            "success": True,
            "player_id": player.player_id,
        })
    finally:
        db.session.close()

    return {
        "success": False
    }


@app.route('/players/<int:player_id>', methods=['PATCH'])
def player_submit(player_id: int):
    """
    :returns
    """
    try:
        data = request.get_json()
        player = Player.query.get(player_id)
        if not player.submit_time:
            player.submit_time = datetime.now()
            player.player_code = zlib.compress(data["player_code"].encode("utf-8"))
            db.session.commit()
        else:
            return jsonify({
                "forgery": check_forgery(player, data["player_code"])
            })
    except:
        db.session.rollback()
        print(sys.exc_info())
        return jsonify({
            "success": False
        })
    else:
        return jsonify({
            "success": True
        })
    finally:
        db.session.close()


def check_forgery(player: Player, new_code: str):
    """
    :returns
    """
    new_code = zlib.compress(new_code.encode("utf-8"))
    original_code = player.player_code
    if original_code != new_code:
        return True

    return False


if __name__ == '__main__':
    app.run()


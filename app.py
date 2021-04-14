from flask import Flask, jsonify

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.sqlite3'

db = SQLAlchemy(app)


class Game(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    category = db.Column(db.String(100), default="War")
    players = db.relationship('Player', lazy=True)


class Player(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class User(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    players = db.relationship('Player', lazy=True)
    interests = db.relationship('Interest', lazy=True)


class Interest(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


def assign_algorithm_score_for(user1, user2):
    # A user starts with 0 points
    # we add points for the similarities in interests
    algo_user = user1.__dict__.copy()
    algo_user['score'] = 0
    for interest in user1.interests:
        if interest.name in [i.name for i in user2.interests]:
            algo_user['score'] += 1
    return algo_user


@app.route('/next-opponent')
def get_next_opponent():
    # Find the current user
    current_user = User.query.filter_by(username='brian').first()

    # Find users who we previously played
    my_players = current_user.players
    games_played = Game.query.filter(Game.id.in_(
        [player.game_id for player in my_players])).all()
    previously_played_with = Player.query.filter(
        Player.game_id.in_([game.id for game in games_played])).all()
    users_played_with = User.query.filter(User.id.in_(
        [player.user_id for player in previously_played_with])).all()

    # Find the best opponent
    potential_users = User.query.filter(User.id.notin_(
        [user.id for user in users_played_with])).all()
    algorithm_scored_users = []
    for user in potential_users:
        scored_user = assign_algorithm_score_for(user, current_user)
        algorithm_scored_users.append(scored_user)

    # sort the users by score, and pluck the one with the top score
    sorted_users = sorted(algorithm_scored_users,
                          key=lambda i: i['score'], reverse=True)
    best_user = sorted_users[0]
    return jsonify(user_id=best_user['id'])


if __name__ == '__main__':
    app.run(debug=True)

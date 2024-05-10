from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:demo@localhost:3306/demo"

db = SQLAlchemy(app)
ma = Marshmallow(app)


# User table model
class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)


with app.app_context():
    db.create_all()


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True


# serialize the data
user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route('/get_user_list', methods=['GET'])
def get_user_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    paginated_users = User.query.paginate(page=page, per_page=per_page)
    users = paginated_users.items
    total_pages = max(paginated_users.pages, 1)

    return make_paginated_response(data=users_schema.dump(users), pages=total_pages)


@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.json['name']
    gender = request.json['gender']

    if not name or not gender:
        return make_response(400, 'Name and Gender are required')

    new_user = User(name=name, gender=gender)
    db.session.add(new_user)
    db.session.commit()
    return make_response(data=user_schema.dump(new_user))


@app.route('/edit_user', methods=['PUT'])
def edit_user():
    uid = request.json['uid']
    user = User.query.get_or_404(uid)
    if not user:
        return make_response(404, 'User not found')

    name = request.json['name']
    gender = request.json['gender']
    if not name or not gender:
        return make_response(400, 'Name and Gender are required')
    user.name = name
    user.gender = gender
    db.session.commit()
    return make_response(data=user_schema.dump(user))


def make_response(code=200, message='Success', data=None):
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    })


def make_paginated_response(code=200, message='Success', data=None, pages=1):
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'pages': pages
    })


if __name__ == '__main__':
    app.run()

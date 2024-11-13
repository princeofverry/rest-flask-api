from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

# Model User
class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"User(name = {self.name}, email = {self.email})"

# Argument Parser
user_args = reqparse.RequestParser()
user_args.add_argument('name', type=str, required=True, help="Name cannot be blank")
user_args.add_argument('email', type=str, required=True, help="Email cannot be blank")

# User Fields
user_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String,
}

# Fungsi untuk validasi email dengan regex
def validate_user_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        abort(400, message="Invalid email format")

# Resource untuk Users
class Users(Resource):
    @marshal_with(user_fields)
    def get(self):
        # Ambil query parameter untuk pencarian
        name_query = request.args.get('name', type=str)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        if name_query:
            # Jika ada query parameter `name`, lakukan pencarian berdasarkan nama
            users = UserModel.query.filter(UserModel.name.ilike(f'%{name_query}%')).paginate(page=page, per_page=per_page, error_out=False)
        else:
            # Jika tidak ada query parameter `name`, ambil semua pengguna
            users = UserModel.query.paginate(page=page, per_page=per_page, error_out=False)

        return users.items  # Mengembalikan data pengguna pada halaman saat ini

    @marshal_with(user_fields)
    def post(self):
        args = user_args.parse_args()
        # Validasi email
        validate_user_email(args['email'])
        user = UserModel(name=args['name'], email=args['email'])
        db.session.add(user)
        db.session.commit()
        return user, 201

# Resource untuk User (berdasarkan ID)
class User(Resource):
    @marshal_with(user_fields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        return user

    @marshal_with(user_fields)
    def put(self, id):
        args = user_args.parse_args()
        # Validasi email
        validate_user_email(args['email'])
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        user.name = args["name"]
        user.email = args["email"]
        db.session.commit()
        return user

    @marshal_with(user_fields)
    def patch(self, id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        if args["name"]:
            user.name = args["name"]
        if args["email"]:
            user.email = args["email"]
        db.session.commit()
        return user

    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        db.session.delete(user)
        db.session.commit()
        return '', 204

# Menambahkan resource ke API
api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:id>')

@app.route('/')
def home():
    return '<h1>Flask REST API</h1>'

if __name__ == '__main__':
    app.run(debug=True)

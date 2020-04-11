from flask import request
from sqlalchemy.exc import IntegrityError
from models import User
from app import app, db
from decorators import json_only, required_args
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt_identity, jwt_refresh_token_required,
                                jwt_required)


@app.route('/health_check', methods=['GET'])
def health_check():
    return {"ok": True}, 200


@app.route('/user', methods=['POST'])
@json_only
@required_args('username', 'name', 'password')
def register_user():
    data = request.get_json()
    username = data.get('username')
    name = data.get('name')
    password = data.get('password')

    try:
        user = User()
        user.username = username
        user.name = name
        user.password = password
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {'ok': False, 'error': 'Username already exists.'}, 400
    except Exception as e:
        db.session.rollback()
        return {'ok': False, 'error': f'{e}'}, 400

    return {'ok': True, 'message': 'User registered successfully'}, 201


@app.route('/auth', methods=['POST'])
@json_only
@required_args('username', 'password')
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter(User.username.ilike(username)).first()
    if (not user) or (not user.check_password(password)):
        return {'ok': False, 'error': 'Username/Password does not match.'}, 403

    access_token = create_access_token(identity=user.username, fresh=True)
    refresh_token = create_refresh_token(identity=user.username)

    return {'ok': True,
            'access_token': access_token,
            'refresh_token': refresh_token}, 200


@app.route('/auth', methods=['PUT'])
@jwt_refresh_token_required
def refresh_access_token():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity, fresh=False)
    return {'ok': True, 'access_token': access_token}, 200


@app.route('/user', methods=['GET'])
@jwt_required
def get_user():
    identity = get_jwt_identity()
    user = User.query.filter(User.username.ilike(identity)).first()
    return {"ok": True, "username": user.username, "name": user.name}, 200

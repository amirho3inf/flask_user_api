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

    access_token = create_access_token(identity=user.id, fresh=True)
    refresh_token = create_refresh_token(identity=user.id)

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
    user = User.query.filter(User.id == identity).first()
    return {"ok": True, "username": user.username, "name": user.name}, 200


@app.route('/user', methods=['PATCH'])
@jwt_required
@json_only
def modify_user():
    data = request.get_json()
    identity = get_jwt_identity()
    user = User.query.filter(User.id == identity).first()

    username = data.get('username')
    name = data.get('name')
    password = data.get('password')

    if not any([username, name, password]):
        return {}, 304

    if username is not None:
        user.username = username

    if name is not None:
        user.name = name

    if password is not None:
        old_password = data.get("old_password")
        if old_password is None:
            return {"ok": False, "error": "old_password required!"}, 400

        if not user.check_password(old_password):
            return {"ok": False, "error": "old password is incorrect!"}, 403

        user.password = password

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {'ok': False, 'error': f'{e}'}, 400

    return {}, 204

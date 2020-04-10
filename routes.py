from flask import request
from sqlalchemy.exc import IntegrityError
from models import User
from app import app, db
from decorators import json_only, required_args


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

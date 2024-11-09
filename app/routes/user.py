from flask import Blueprint, request, jsonify

from flask_jwt_extended import (
    create_access_token,
    jwt_required, get_jwt
)
from flasgger import swag_from
from datetime import datetime
from app import db
from app.models.user import User
from app.utils.auth_helpers import revoke_token
user_api = Blueprint('user_api', __name__)


@user_api.route('/register', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Register a new user',
    'description': 'Create a new user account',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'description': "User's username"},
                    'password': {'type': 'string', 'description': "User's password"}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        },
        400: {
            'description': 'Invalid input'
        }
    }
})
def register():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400

    user = User(username=data['username'])
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201


@user_api.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Login user',
    'description': 'Login with username and password to get JWT token',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'description': "User's username"},
                    'password': {'type': 'string', 'description': "User's password"}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Login successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'access_token': {'type': 'string'}
                }
            }
        },
        401: {
            'description': 'Invalid credentials'
        }
    }
})
def login():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=user.username)
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token
    }), 200


@user_api.route('/logout', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Logout user',
    'description': 'Logout the current user (invalidates token client-side)',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'Logout successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        },
        401: {
            'description': 'Invalid token'
        }
    }
})
def logout():
    try:
        jti = get_jwt()["jti"]
        revoke_token(jti)
        return jsonify({
            'message': 'Token revoked',
            'logout_at': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'message': 'Logout failed',
            'error': str(e)
        }), 500



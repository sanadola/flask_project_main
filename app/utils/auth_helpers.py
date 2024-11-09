from flask_jwt_extended import get_jwt
from datetime import datetime
from functools import wraps
from flask import jsonify

from app import db
from app.models.user import TokenBlocklist


def revoke_token(jti):
    """Helper function to revoke a token"""
    try:
        token = TokenBlocklist(jti=jti, created_at=datetime.utcnow())
        db.session.add(token)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise e

def is_token_revoked(jti):
    return TokenBlocklist.query.filter_by(jti=jti).first() is not None

def check_token_revoked(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            jwt = get_jwt()
            if is_token_revoked(jwt['jti']):
                return jsonify({
                    'message': 'Token has been logged out',
                    'error': 'invalid_token'
                }), 401                
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'message': 'Error checking token status',
                'error': str(e)
            }), 500
    
    return wrapper
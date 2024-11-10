from datetime import datetime
from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship

from app import db



class ImageModel(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(80), nullable=True)
    image_data = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('images', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'image_name': self.image_name,
            'image_data': self.image_data,
            'created_at': self.created_at.isoformat(),
            'user': self.user.to_dict() if self.user else None  # Include user info if available
        }
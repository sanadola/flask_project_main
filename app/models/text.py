from datetime import datetime
from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from app import db

class Text(db.Model):
    __tablename__ = 'text'
    id = db.Column(db.Integer, primary_key=True)
    headline = db.Column(db.String(255), nullable=True)
    text_body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Foreign key relationship with User model
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", backref="text")

    def to_dict(self):
        return {
            'id': self.id,
            'headline': self.headline,
            'text_body': self.text_body,
            'created_at': self.created_at.isoformat(),
            'user': self.user.to_dict() if self.user else None  # Include user info if available

        }
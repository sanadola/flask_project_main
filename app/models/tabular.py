from datetime import datetime
from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from app import db

class TabularData(db.Model):
    __tablename__ = 'tabular'
    id = db.Column(db.Integer, primary_key=True)
    tabular_name = db.Column(db.String(100))
    tabular_data = db.Column(db.LargeBinary)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", backref="tabular")

    def to_dict(self):
        return {
            'id': self.id,
            'tabular_name': self.tabular_name,
            'tabular_data': self.tabular_data,
            'created_at': self.created_at.isoformat(),
            'user': self.user.to_dict() if self.user else None  # Include user info if available

        }
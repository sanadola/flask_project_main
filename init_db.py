from app import create_app, db
from app.models.user import User
from app.models.tabular import TabularData
from app.models.text import Text
from app.models.image import Image


def init_db():
    app = create_app()
    with app.app_context():
        print("Dropping all existing tables...")
        db.drop_all()  # Be careful with this in production!
        
        print("Creating all tables...")
        db.create_all()
        
        print("Tables created:")
        for table in db.metadata.tables.keys():
            print(f"- {table}")
        
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin')
            admin.set_password('admin123')  # In production, use a secure password
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists!")
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
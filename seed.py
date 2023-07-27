from models import db, connect_db, User, Feedback
from app import app

def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        user = User.register(username="JustB544", first_name="Breyton", last_name="Pabst", email="breytonpabst@gmail.com", password="howdy")

        db.session.add(user)
        db.session.commit()

        feedback = Feedback(title="idk", content="I really don't know", username="JustB544")

        db.session.add(feedback)
        db.session.commit()


seed()

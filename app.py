from flask import Flask
from application.database import db
app = None

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.sqlite3"
    db.init_app(app)
    app.app_context().push()
    return app

app = create_app()
#importing controllers.py only after app object gets created inside app.py
from application.controllers import *
if __name__ == '__main__':
    # db.create_all()
    # user1=User(username="admin1", email="admin@mail.com", password="xyz", type="admin")
    # db.session.add(user1)
    # db.session.commit()
    app.run()
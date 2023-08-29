from exts import db
from utils import gen_short_id


class User(db.Document):
    name = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True, unique=True)
    role = db.StringField(choices=["staff", "tourist", "bot"])
    display_picture = db.StringField()

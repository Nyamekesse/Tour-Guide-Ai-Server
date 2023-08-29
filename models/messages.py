from exts import db


class Message(db.Document):
    author = db.ReferenceField("User")
    content = db.StringField()
    date = db.DateTimeField()

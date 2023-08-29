from exts import db


class Conversation(db.Document):
    participants = db.ListField(db.ReferenceField("User"))
    messages = db.ListField(db.ReferenceField("Message"))

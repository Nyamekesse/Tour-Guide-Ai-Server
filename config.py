from decouple import config

USERNAME = config("MONGO_USERNAME")
PASSWORD = config("MONGO_PASSWORD")


class Config:
    SECRET_KEY = config("SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = False
    MONGODB_SETTINGS = {
        "host": "mongodb+srv://nyamekessesamuel:5lhk8daQJh4bhHvB@cluster0.bqi5lvt.mongodb.net/?retryWrites=true&w=majority"
    }


class DevConfig(Config):
    pass


class ProConfig(Config):
    pass


class TestConfig(Config):
    pass

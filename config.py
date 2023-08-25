from decouple import config


DB_NAME = config("DB_NAME")
DB_TESTING_NAME = config("DB_TESTING_NAME")
DB_USERNAME = config("DB_USERNAME")
DB_USER_PASS = config("DB_USER_PASS")
DB_CONNECTION_PORT = config("DB_CONNECTION_PORT")


class Config:
    SECRET_KEY = config("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = config("SQLALCHEMY_TRACK_MODIFICATIONS", cast=bool)


class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USERNAME}:{DB_USER_PASS}@{DB_CONNECTION_PORT}/{DB_NAME}"
    )
    DEBUG = config("DEBUG", cast=bool)
    # SQLALCHEMY_ECHO = config("SQLALCHEMY_ECHO", cast=bool)


class ProConfig(Config):
    pass


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USERNAME}:{DB_USER_PASS}@{DB_CONNECTION_PORT}/{DB_TESTING_NAME}"
    SQLALCHEMY_ECHO = False
    TESTING = True

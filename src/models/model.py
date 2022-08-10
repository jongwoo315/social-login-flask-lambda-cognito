from datetime import datetime
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from config import DevelopmentConfig

try:
    os.environ['AWS_EXECUTION_ENV']
except KeyError:
    database_uri = DevelopmentConfig.SQLALCHEMY_DATABASE_URI_LOCAL
else:
    database_uri = DevelopmentConfig.SQLALCHEMY_DATABASE_URI

engine = create_engine(database_uri)
Base = declarative_base(engine)


class User(Base):
    __tablename__ = 'cognito_users'
    idx  = Column('idx', Integer, primary_key=True)
    sub = Column(String(60))
    cognito_username = Column(String(30))
    platform = Column(String(30))
    user_id = Column(String(60))
    email = Column(String(100), nullable=True)
    screen_name = Column(String(60))
    profile_image_url = Column(String(1000))
    regist_date = Column(DateTime, default=datetime.now())
    update_date = Column(DateTime, default=datetime.now())

    UniqueConstraint(sub, name='sub_idx')

    def __init__(
            self,
            sub,
            cognito_username,
            platform,
            user_id,
            screen_name,
            profile_image_url,
            email
        ):  
        self.sub = sub
        self.cognito_username = cognito_username
        self.platform = platform
        self.user_id = user_id
        self.email = email
        self.screen_name = screen_name
        self.profile_image_url = profile_image_url

Base.metadata.create_all(bind=engine)
db_session = Session(bind=engine)

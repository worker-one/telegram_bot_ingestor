import datetime
import logging
import os

from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base, Message, User


logger = logging.getLogger(__name__)

load_dotenv(find_dotenv(usecwd=True))

# Retrieve environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Check if any of the required environment variables are not set
if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
    logger.error("One or more database environment variables are not set.")
    exit(1)

# Construct the database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


def create_tables():
	Base.metadata.create_all(engine)


def log_message(user_id, message_text):
	session = Session()
	new_message = Message(
		timestamp=datetime.datetime.now(),
		user_id=user_id,
		message_text=message_text
	)
	session.add(new_message)
	session.commit()


def add_user(user_id, first_name, last_name, username, phone_number):
	session = Session()
	new_user = User(
		user_id=user_id,
		first_message_timestamp=datetime.datetime.now(),
		first_name=first_name,
		last_name=last_name,
		username=username,
		phone_number=phone_number
	)
	# add only if the user is not already in the database
	if not session.query(User).filter(User.user_id == user_id).first():
		session.add(new_user)
	session.commit()

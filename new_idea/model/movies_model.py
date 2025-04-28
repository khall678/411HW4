import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from movies.db import db
from movies.utils.logger import configure_logger
from movies.utils.api_utils import get_random

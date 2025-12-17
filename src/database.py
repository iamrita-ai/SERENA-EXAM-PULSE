from pymongo import MongoClient
from .config import config

_client = MongoClient(config.mongo_uri)
_db = _client[config.mongo_db_name]


def get_db():
    return _db


def get_users_collection():
    return _db["users"]


def get_blocked_collection():
    return _db["blocked_users"]


def get_exams_collection():
    """Exam / job notifications ke liye collection."""
    return _db["exams"]

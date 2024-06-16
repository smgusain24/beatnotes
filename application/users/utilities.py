import bcrypt
from config.app_logger import logger
from config.mysql import execute_insert_query, execute_read_query


def hash_password(password: str) -> bytes:
    try:
        password = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password, salt)
        return hashed_password
    except Exception as e:
        logger.error(e, exc_info=True, stack_info=True)


def verify_password(user_password: str, hashed_password: bytes) -> bool:
    try:
        user_password = user_password.encode('utf-8')
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        if bcrypt.checkpw(user_password, hashed_password):
            return True
        else:
            return False
    except Exception as e:
        logger.error(e, exc_info=True, stack_info=True)


def create_user(username: str, email: str, hashed_password: bytes) -> any:
    try:
        query = "INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s)"
        params = (username, email, hashed_password)
        user_id = execute_insert_query(query=query, params=params)
        if user_id:
            return user_id
        return None
    except Exception as e:
        logger.error(e, exc_info=True)


def fetch_user_data_by_param(param, value) -> dict:
    try:
        query = f"SELECT * FROM users WHERE {param} = %s"
        result = execute_read_query(query=query, params=(value,), cursor='dict')
        if result:
            return result[0]
        return {}
    except Exception as e:
        logger.error(e, exc_info=True)
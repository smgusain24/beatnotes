from datetime import datetime

from fastapi.requests import Request
from fastapi.responses import JSONResponse

from application.users.utilities import hash_password, create_user, fetch_user_data_by_param, verify_password
from config.app_logger import logger
from config.auth import generate_jwt_token
from config.http_status import *
from fastapi import APIRouter, Response

from config.mysql import execute_update_query
from constants import _VERSION

router = APIRouter(prefix=f"/{_VERSION}/users", tags=['Users'])


@router.post("/signup")
async def signup(request: Request):
    try:
        data = await request.form()
        username: str = data.get('username')
        password: str = data.get('password')
        email: str = data.get('email')

        flag = fetch_user_data_by_param(param='username', value=username)
        if flag:
            return JSONResponse(content={'msg': 'User already exists'}, status_code=HTTP_409_CONFLICT)
        hashed_password = hash_password(password)
        user_id = create_user(username, email, hashed_password)
        return JSONResponse(content=f"User created with id : {user_id}", status_code=HTTP_201_CREATED)
    except Exception as e:
        logger.error(e, exc_info=True, stack_info=True)
        return JSONResponse(content={'msg': f'{e}'}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/login")
async def user_login(request: Request, response: Response):
    try:
        data = await request.form()
        username: str = data.get('username')
        user_password: str = data.get('password')

        user = fetch_user_data_by_param(param='username', value=username)
        if not user:
            return JSONResponse(content={'msg': 'User does not exist'}, status_code=HTTP_400_BAD_REQUEST)

        hashed_password = user['hashed_password']
        if not verify_password(user_password, hashed_password):
            return JSONResponse(content={'msg': 'Invalid credentials'}, status_code=HTTP_401_UNAUTHORIZED)

        user_details = {
            "user_id": user['id'],
            "is_active": user['is_active'],
            "is_admin": user['is_admin'],
            "email": user['email'],
            "username": username
        }

        access_token = generate_jwt_token(user_details=user_details, time_in_minutes=120)
        refresh_token = generate_jwt_token(user_details=user_details, time_in_minutes=86400, token_type='refresh')

        query = "UPDATE users SET last_login = %s WHERE username = %s"
        params = (datetime.now(), username)
        execute_update_query(query=query, params=params)

        login_response = JSONResponse(content={'msg': 'Logged in successfully'}, status_code=HTTP_200_OK)
        login_response.headers["Auth-Token"] = access_token
        login_response.headers["Refresh-Token"] = refresh_token

        return login_response

    except Exception as e:
        logger.error(e, exc_info=True, stack_info=True)
        return JSONResponse(content={'msg': 'Internal server error'}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)


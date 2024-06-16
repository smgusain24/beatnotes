from fastapi.requests import Request
from fastapi.responses import JSONResponse

from config.app_logger import logger
from config.auth import  access_token_required
from config.http_status import *
from fastapi import APIRouter

from config.mysql import execute_update_query, execute_read_query
from constants import _VERSION
from .utilities import create_board, create_note, process_boards_notes

router = APIRouter(prefix=f"/{_VERSION}/editor", tags=['Editor'])


# Boards functionality

@router.post("/boards")
@access_token_required
async def post_board(request: Request):
    try:
        data = await request.json()
        user_data: dict = request.state.user_details

        user_id: int = user_data['user_id']
        title: str = data.get('title')
        description: str = data.get('description', '')
        icon_id: int = int(data['icon_id']) if data.get('icon_id') else 0
        board_id = create_board(user_id, title, description, icon_id)
        if board_id:
            return JSONResponse(content={'msg': f'Board created ID: {board_id}'}, status_code=HTTP_201_CREATED)
        else:
            raise Exception('Board not created, query error!')

    except Exception as e:
        logger.error(e, exc_info=True, stack_info=True)
        return JSONResponse(content={'msg': f'{e}'}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)


@router.get('/boards')
@access_token_required
async def get_boards(request: Request):
    try:
        user_data: dict = request.state.user_details
        user_id: int = user_data['user_id']
        query = """
            SELECT
              b.id AS board_id,
              b.icon_id AS board_icon_id,
              b.title AS board_title,
              b.description AS board_description,
              n.id AS note_id,
              n.icon_id AS note_icon_id,
              n.title AS note_tile,
              n.content AS note_content,
              n.x_position,
              n.y_position
            FROM
              boards b
              JOIN notes n ON n.board_id = b.id
            WHERE
              n.is_active = 1
              AND b.is_active = 1
              AND b.user_id = %s
        """
        params = (user_id,)
        boards = execute_read_query(query=query, params=params, cursor='dict')
        if boards:
            boards_list = process_boards_notes(boards)
            return JSONResponse(content=boards_list, status_code=HTTP_200_OK)
        else:
            return JSONResponse(content=[], status_code=HTTP_200_OK)

    except Exception as e:
        logger.error(e, exc_info=True, stack_info=True)
        return JSONResponse(content={'msg': f'{e}'}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)


#   Notes functionality

@router.post('/post_note')
@access_token_required
async def post_note(request: Request):
    try:
        data = await request.form()
        user_data: dict = request.state.user_details
        user_id: int = user_data['user_id']

        # Notes data
        board_id: int = int(data['board_id'])
        title: str = data.get('title', '')
        icon_id: int = int(data['icon_id']) if data.get('icon_id') else 0
        content: str = data.get('content', '')
        x_position: int = int(data['x_position'])
        y_position: int = int(data['y_position'])

        # Create Note
        note_id = create_note(board_id, title, icon_id, content, x_position, y_position)
        if note_id:
            return JSONResponse(content={'msg': f'Note created ID: {note_id}'}, status_code=HTTP_201_CREATED)
        else:
            raise Exception('Note not created, query error!')
    except Exception as e:
        logger.erorr(e, exc_info=True)
        return JSONResponse(content={'msg': f'{e}'}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)


@router.put('/edit_note')
@access_token_required
async def get_note(request: Request):
    try:

        data = await request.form()
        note_id: int = int(data['note_id'])

        # Initialize the query and params
        query = "UPDATE notes SET"
        params = []

        # Retrieve values that are being updated
        if 'icon_id' in data:
            query += " icon_id = %s,"
            params.append(int(data['icon_id']))
        if 'title' in data:
            query += " title = %s,"
            params.append(data['title'])
        if 'content' in data:
            query += " content = %s,"
            params.append(data['content'])
        if 'x_position' in data:
            query += " x_position = %s,"
            params.append(data['x_position'])
        if 'y_position' in data:
            query += " y_position = %s,"
            params.append(data['y_position'])

        # Remove the last comma from the query
        query = query.rstrip(',')

        # Add  WHERE clause to the query
        query += " WHERE id = %s"
        params.append(note_id)

        flag = execute_update_query(query=query, params=tuple(params))
        if flag:
            return JSONResponse(content={'msg': 'Note updated!'}, status_code=HTTP_200_OK)
        else:
            raise Exception('Note not updated, query error!')
    except Exception as e:
        logger.error(e, exc_info=True)
        return JSONResponse(content={'msg': f'{e}'}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)


@router.delete('/delete_note')
@access_token_required
async def delete_note(request: Request):
    try:
        data = await request.json()
        note_id: int = int(data['note_id'])
        query = "UPDATE notes SET is_active = 0 WHERE id = %s"
        params = (note_id,)
        flag = execute_update_query(query=query, params=params)
        if flag:
            return JSONResponse(content={'msg': 'Note deleted!'}, status_code=HTTP_200_OK)
        else:
            raise Exception('Note not deleted, query error!')
    except Exception as e:
        logger.error(e, exc_info=True)
        return JSONResponse(content={'msg': f'{e}'}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)



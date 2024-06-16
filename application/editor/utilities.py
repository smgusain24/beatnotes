from config.app_logger import logger
from config.mysql import execute_insert_query


def create_board(user_id, title, description, icon_id) -> any:
    try:
        query = """
                    INSERT INTO boards 
                    (user_id, title,  description, icon_id)
                    VALUES
                    (%s, %s, %s, %s)
                """
        params = (user_id, title, description, icon_id)
        board_id = execute_insert_query(query=query, params=params)
        return board_id
    except Exception as e:
        logger.error(e, exc_info=True)
        return None


def create_note(board_id, title, icon_id, content, x_position, y_position) -> any:
    try:
        query = """
            INSERT INTO notes
            (board_id, title, icon_id, content, x_position, y_position)
            VALUES 
            (%s, %s, %s, %s, %s, %s)
        """
        params = (board_id, title, icon_id, content, x_position, y_position)
        note_id = execute_insert_query(query=query, params=params)
        return note_id
    except Exception as e:
        logger.error(e, exc_info=True)
        return None


def process_boards_notes(boards) -> list:
    try:
        board_dict = {}
        for row in boards:
            board_id = row['board_id']
            if board_id not in board_dict:
                board_dict[board_id] = {
                    'board_id': board_id,
                    'board_icon_id': row['board_icon_id'],
                    'board_title': row['board_title'],
                    'board_description': row['board_description'],
                    'notes': []
                }

            note = {
                'note_id': row['note_id'],
                'note_icon_id': row['note_icon_id'],
                'note_title': row['note_tile'],
                'note_content': row['note_content'],
                'x_position': row['x_position'],
                'y_position': row['y_position']
            }
            board_dict[board_id]['notes'].append(note)

        return list(board_dict.values())
    except Exception as e:
        logger.error(e, exc_info=True)
        return []

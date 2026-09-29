from connection import db_connector


def create_comment(discussion_id, user_id, content):
    con = db_connector()
    cursor = con.cursor()

    query = """
        INSERT INTO comments (discussion_id, user_id, content)
        VALUES (%s, %s, %s)
    """

    cursor.execute(query, (discussion_id, user_id, content))
    con.commit()

    comment_id = cursor.lastrowid

    cursor.close()
    con.close()

    return comment_id


def get_comments_by_discussion(discussion_id):
    con = db_connector()
    cursor = con.cursor(dictionary=True)

    query = """
        SELECT c.*, u.name AS author_name
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.discussion_id = %s
        ORDER BY c.created_at DESC
    """

    cursor.execute(query, (discussion_id,))
    results = cursor.fetchall()

    cursor.close()
    con.close()

    return results

from connection import db_connector


def create_discussion(issue_id, user_id, title, content):
    con = db_connector()
    cursor = con.cursor()

    query = """
        INSERT INTO discussions (issue_id, user_id, title, content)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(query, (issue_id, user_id, title, content))
    con.commit()

    discussion_id = cursor.lastrowid

    cursor.close()
    con.close()

    return discussion_id


def get_discussions_by_issue(issue_id):
    con = db_connector()
    cursor = con.cursor(dictionary=True)

    query = """
        SELECT d.*, u.name AS author_name
        FROM discussions d
        JOIN users u ON d.user_id = u.id
        WHERE d.issue_id = %s
        ORDER BY d.created_at DESC
    """

    cursor.execute(query, (issue_id,))
    results = cursor.fetchall()

    cursor.close()
    con.close()

    return results


def get_discussion_by_id(discussion_id):
    con = db_connector()
    cursor = con.cursor(dictionary=True)

    query = """
        SELECT d.*, u.name AS author_name
        FROM discussions d
        JOIN users u ON d.user_id = u.id
        WHERE d.id = %s
    """

    cursor.execute(query, (discussion_id,))
    result = cursor.fetchone()

    cursor.close()
    con.close()

    return result

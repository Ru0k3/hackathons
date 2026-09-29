from connection import db_connector


def create_issue(title, summary, category_id):
    conn = db_connector()
    cursor = conn.cursor()

    query = """
        INSERT INTO issues (title, summary, category_id)
        VALUES (%s, %s, %s)
    """

    cursor.execute(query, (title, summary, category_id))
    conn.commit()

    issue_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return issue_id


def get_all_issues(category_id=None, sort=None):
    con = db_connector()
    cursor = con.cursor(dictionary=True)

    query = """
        SELECT issues.*, categories.name AS category_name
        FROM issues
        JOIN categories ON issues.category_id = categories.id
    """
    params = []

    if category_id is not None:
        query += " WHERE issues.category_id = %s"
        params.append(category_id)

    if sort == "latest":
        query += " ORDER BY issues.created_at DESC"
    else:
        query += " ORDER BY issues.id DESC"

    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    con.close()
    print(results)
    return results


def get_issue_by_id(issue_id):
    con = db_connector()
    cursor = con.cursor(dictionary=True)

    query = """
        SELECT issues.*, categories.name AS category_name
        FROM issues
        JOIN categories ON issues.category_id = categories.id
        WHERE issues.id = %s
    """

    cursor.execute(query, (issue_id,))
    result = cursor.fetchone()

    cursor.close()
    con.close()

    return result

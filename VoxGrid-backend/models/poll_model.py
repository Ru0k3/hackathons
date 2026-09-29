from connection import db_connector


def create_poll(issue_id, question):
    conn = db_connector()
    cursor = conn.cursor()

    query = """
        INSERT INTO polls (issue_id, question)
        VALUES (%s, %s)
    """

    cursor.execute(query, (issue_id, question))
    conn.commit()

    poll_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return poll_id


def add_poll_options(poll_id, options):
    conn = db_connector()
    cursor = conn.cursor()

    query = """
        INSERT INTO poll_options (poll_id, option_text)
        VALUES (%s, %s)
    """

    for option in options:
        cursor.execute(query, (poll_id, option))

    conn.commit()
    cursor.close()
    conn.close()


def vote_poll(poll_id, option_id):
    conn = db_connector()
    cursor = conn.cursor()

    query = """
        INSERT INTO poll_votes (poll_id, option_id)
        VALUES (%s, %s)
    """

    cursor.execute(query, (poll_id, option_id))
    conn.commit()

    cursor.close()
    conn.close()


def get_poll_by_issue(issue_id):
    conn = db_connector()
    cursor = conn.cursor(dictionary=True)

    # get poll
    cursor.execute("SELECT * FROM polls WHERE issue_id = %s", (issue_id,))
    poll = cursor.fetchone()

    if not poll:
        cursor.close()
        conn.close()
        return None

    poll_id = poll["id"]

    # get options + vote counts
    query = """
        SELECT po.id, po.option_text, COUNT(pv.id) as votes
        FROM poll_options po
        LEFT JOIN poll_votes pv ON po.id = pv.option_id
        WHERE po.poll_id = %s
        GROUP BY po.id
    """

    cursor.execute(query, (poll_id,))
    options = cursor.fetchall()

    poll["options"] = options

    cursor.close()
    conn.close()

    return poll


def get_poll_results(poll_id):
    conn = db_connector()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT po.id, po.option_text, COUNT(pv.id) as votes
        FROM poll_options po
        LEFT JOIN poll_votes pv ON po.id = pv.option_id
        WHERE po.poll_id = %s
        GROUP BY po.id
    """

    cursor.execute(query, (poll_id,))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results


def get_poll_by_id(poll_id):
    con = db_connector()
    cursor = con.cursor(dictionary=True)

    query = "SELECT * FROM polls WHERE id = %s"

    cursor.execute(query, (poll_id,))
    poll = cursor.fetchone()

    cursor.close()
    con.close()

    return poll


def get_poll_options(poll_id):
    con = db_connector()
    cursor = con.cursor(dictionary=True)

    query = """
        SELECT *
        FROM poll_options
        WHERE poll_id = %s
    """

    cursor.execute(query, (poll_id,))
    options = cursor.fetchall()

    cursor.close()
    con.close()

    return options

from connection import db_connector


def fetch_categories():
    conn = db_connector()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT *
        FROM categories
        ORDER BY name ASC
    """

    cursor.execute(query)

    categories = cursor.fetchall()

    cursor.close()
    conn.close()

    return categories

from connection import db_connector


def add_user(name, email, password, avatar_url=None):
    con = db_connector()
    cursor = con.cursor()

    try:
        query = """
            INSERT INTO users (name, email, password, avatar_url)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (name, email, password, avatar_url))
        con.commit()

        return {"success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}

    finally:
        cursor.close()
        con.close()


def login_user(email, password):
    con = db_connector()
    cursor = con.cursor(dictionary=True)

    query = """
        SELECT * FROM users WHERE email = %s AND password = %s
    """
    cursor.execute(query, (email, password))

    user = cursor.fetchone()

    cursor.close()
    con.close()

    return user

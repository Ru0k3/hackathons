from connection import db_connector


def fetch_blogs(issue_id=None):

    conn = db_connector()

    cursor = conn.cursor(dictionary=True)

    if issue_id:

        query = """
            SELECT
                blogs.*,
                users.name AS author_name
            FROM blogs

            JOIN users
            ON blogs.user_id = users.id

            WHERE issue_id = %s

            ORDER BY created_at DESC
        """

        cursor.execute(query, (issue_id,))

    else:

        query = """
            SELECT
                blogs.*,
                users.name AS author_name
            FROM blogs

            JOIN users
            ON blogs.user_id = users.id

            ORDER BY created_at DESC
        """

        cursor.execute(query)

    blogs = cursor.fetchall()

    cursor.close()
    conn.close()

    return blogs


def fetch_blog_by_id(blog_id):

    conn = db_connector()

    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            blogs.*,
            users.name AS author_name
        FROM blogs

        JOIN users
        ON blogs.user_id = users.id

        WHERE blogs.id = %s
    """

    cursor.execute(query, (blog_id,))

    blog = cursor.fetchone()

    cursor.close()
    conn.close()

    return blog


def add_blog(issue_id, user_id, title, content):

    conn = db_connector()

    cursor = conn.cursor()

    query = """
        INSERT INTO blogs (
            issue_id,
            user_id,
            title,
            content
        )

        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(query, (issue_id, user_id, title, content))

    conn.commit()

    blog_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return blog_id

from connection import db_connector


def add_vote(target_type, target_id, vote_type):
    conn = db_connector()
    cursor = conn.cursor()

    query = """
        INSERT INTO votes (target_type, target_id, vote_type)
        VALUES (%s, %s, %s)
    """

    cursor.execute(query, (target_type, target_id, vote_type))
    conn.commit()

    cursor.close()
    conn.close()


def get_vote_counts(target_type, target_id):
    conn = db_connector()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT vote_type, COUNT(*) as count
        FROM votes
        WHERE target_type = %s AND target_id = %s
        GROUP BY vote_type
    """

    cursor.execute(query, (target_type, target_id))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    # format response
    counts = {"agree": 0, "disagree": 0}
    for row in results:
        counts[row["vote_type"]] = row["count"]

    return counts

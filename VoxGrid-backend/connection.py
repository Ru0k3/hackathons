import mysql.connector


def db_connector():
    return mysql.connector.connect(
        user="root",
        host="localhost",
        password="1234567890",
        database="vox_grid",
    )

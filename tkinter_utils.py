import mysql.connector
from mysql.connector import Error


def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='new_schema',
            user='root',
            password='root'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None


def execute_query(query, params=None):
    connection = create_connection()
    if connection is None:
        return None

    cursor = connection.cursor(buffered=True)
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()

        if cursor.description is not None:
            return cursor.fetchall()
        else:
            return "Query executed successfully"
    except Error as e:
        print(f"Error: '{e}'")
        return None
    finally:
        cursor.close()
        connection.close()

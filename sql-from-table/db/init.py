import psycopg2


db = psycopg2.connect(
    host="localhost",
    database="vehicle-forum-local",
    port="5432",
    user="postgres",
    password="postgres",
)


def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="vehicle-forum-local",
        port="5432",
        user="postgres",
        password="postgres",
    )


def run_query(query, params=None, fetch=False):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch:
                return cur.fetchall()
            conn.commit()

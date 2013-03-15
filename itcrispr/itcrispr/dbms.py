"""SQLite Database functions"""
import sqlite3


def create_traces_table(db):
    """Create table traces in the given database if it is absent."""
    con, cur = connect(db)
    sql = """select exists(select 1 from sqlite_master where \
    name='traces' and type='table')"""
    exists = cur.execute(sql).fetchone()[0]
    created = False
    if not exists:
        sql = """\
        CREATE TABLE traces
        (
        id integer primary key autoincrement,
        key character varying,
        gene character varying,
        database character varying,
        username character varying,
        date timestamp without time zone,
        status character varying,
        primer character varying
        )"""
        cur.execute(sql)
        con.commit()
        created = True
    return created


def connect(db):
    """Create and/or connect to the given database"""
    con = cur = None
    con = sqlite3.connect(db)
    cur = con.cursor()
    return con, cur


def execute(cursor, query, params=None, executemany=False):
    """Execute database query. Returns None on success and error
    message if failed

    """
    error = None
    if not params:
        params = []
    try:
        if not len(params):
            cursor.execute(query)
        else:
            if executemany:
                cursor.executemany(query, params)
            else:
                cursor.execute(query, params)
    except Exception as e:
        error = str(e)
        conn = cursor.connection
        conn.rollback()
    return error

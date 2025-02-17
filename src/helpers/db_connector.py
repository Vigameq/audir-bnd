import psycopg2

from src.helpers import load_env
from src.format.psql_creds import PsqlCreds

def write_query(query, environment):
    db_vars = load_env.db_env(environment)

    db_creds = PsqlCreds(
        user_name=db_vars['username'],
        password=db_vars['password'],
        host=db_vars['host'],
        database=db_vars['database'],
        port=db_vars['port'],
        sslmode=db_vars['sslmode']
    )

    try:

        con = psycopg2.connect(database=db_creds.database, user=db_creds.user_name,
                               password=db_creds.password, host=db_creds.host,
                               port=db_creds.port, sslmode=db_creds.sslmode)

        cur = con.cursor()
        query_results = cur.execute(query)
        con.commit()
        con.close()

        return query_results, 200
    except Exception as e:
        return str(e), 400


def bulk_write_query(query, params, environment):
    db_vars = load_env.db_env(environment)

    db_creds = PsqlCreds(
        user_name=db_vars['username'],
        password=db_vars['password'],
        host=db_vars['host'],
        database=db_vars['database'],
        port=db_vars['port'],
        sslmode=db_vars['sslmode']
    )

    try:

        con = psycopg2.connect(database=db_creds.database, user=db_creds.user_name,
                               password=db_creds.password, host=db_creds.host,
                               port=db_creds.port, sslmode=db_creds.sslmode)

        cur = con.cursor()
        query_results = cur.executemany(query, params)
        con.commit()
        con.close()

        return query_results, 200
    except Exception as e:
        return str(e), 400

def read_one_query(query, environment):
    db_vars = load_env.db_env(environment)

    db_creds = PsqlCreds(
        user_name=db_vars['username'],
        password=db_vars['password'],
        host=db_vars['host'],
        database=db_vars['database'],
        port=db_vars['port'],
        sslmode=db_vars['sslmode']
    )

    try:

        con = psycopg2.connect(database=db_creds.database, user=db_creds.user_name,
                               password=db_creds.password, host=db_creds.host,
                               port=db_creds.port, sslmode=db_creds.sslmode)

        cur = con.cursor()
        cur.execute(query)
        query_results = cur.fetchone()
        con.close()

        return query_results, 200
    except Exception as e:
        return str(e), 400


def read_all_query(query, environment):
    db_vars = load_env.db_env(environment)

    db_creds = PsqlCreds(
        user_name=db_vars['username'],
        password=db_vars['password'],
        host=db_vars['host'],
        database=db_vars['database'],
        port=db_vars['port'],
        sslmode=db_vars['sslmode']
    )

    try:

        con = psycopg2.connect(database=db_creds.database, user=db_creds.user_name,
                               password=db_creds.password, host=db_creds.host,
                               port=db_creds.port, sslmode=db_creds.sslmode)

        cur = con.cursor()
        cur.execute(query)
        query_results = cur.fetchall()
        con.close()

        return query_results, 200
    except Exception as e:
        return str(e), 400
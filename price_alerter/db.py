import sqlite3


def create_pricelog_table(cursor: sqlite3.Cursor):
    sql = """
    --begin-sql
        CREATE TABLE IF NOT EXISTS pricelog (
            product_name TEXT,
            store TEXT,
            url TEXT,
            target_price DECIMAL,
            current_price DECIMAL,
            status TEXT,
            info TEXT,
            timestamp_added TIMESTAMP
        )
    --end-sql
    """

    cursor.execute(sql)


def create_notifications_table(cursor: sqlite3.Cursor):
    sql = """
    --begin-sql
        CREATE TABLE IF NOT EXISTS notifications (
            product_name TEXT,
            store TEXT,
            url TEXT,
            type TEXT,
            message TEXT,
            timestamp_sent TIMESTAMP
        )
    --end-sql
    """

    cursor.execute(sql)


def create_tables(cursor: sqlite3.Cursor):
    create_pricelog_table(cursor)
    create_notifications_table(cursor)


def add_pricelog_record(
    cursor: sqlite3.Cursor,
    product_name: str,
    store: str,
    url: str,
    target_price: float,
    current_price: float,
    status: str,
    info: str,
):
    sql = """
    --begin-sql
        INSERT INTO pricelog
        (product_name, store, url, target_price, current_price, status, info, timestamp_added)
        VALUES
        (?, ?, ?, ?, ?, ?, ?, datetime(current_timestamp, 'localtime'))
    --end-sql
    """

    cursor.execute(
        sql,
        (
            product_name,
            store,
            url,
            target_price,
            current_price,
            status,
            info,
        ),
    )


def add_notification_record(
    cursor: sqlite3.Cursor,
    product_name: str,
    store: str,
    url: str,
    type: str,
    message: str,
):
    sql = """
    --begin-sql
        INSERT INTO notifications
        (product_name, store, url, type, message, timestamp_sent)
        VALUES
        (?, ?, ?, ?, ?, datetime(current_timestamp, 'localtime'))
    --end-sql
    """

    cursor.execute(
        sql,
        (
            product_name,
            store,
            url,
            type,
            message,
        ),
    )


def get_rows_for_graphs(cursor: sqlite3.Cursor):
    sql = """
    --begin-sql
        SELECT product_name, store, current_price, timestamp_added
        FROM pricelog
        WHERE info = "OK"
        ORDER BY product_name, timestamp_added desc
    --end-sql
    """

    cursor.execute(sql)
    return cursor.fetchall()


def has_been_at_least_2_target_live_records_in_last_day(
    cursor: sqlite3.Cursor, product_name: str, store: str
):
    # return 1 if there are at least 2 target price live records of the product and store that have
    # been recorded in the last day
    sql = """
    --begin-sql
        SELECT 1
        FROM pricelog
        WHERE product_name = ?
            AND store = ?
            AND current_price <= target_price
            AND status != 'ERROR'
            AND timestamp_added BETWEEN datetime(current_timestamp, '-1 days', 'localtime') AND datetime(current_timestamp, 'localtime')
        GROUP BY product_name
        HAVING count(*) > 1
        LIMIT 1
    --end-sql
    """
    cursor.execute(
        sql,
        (
            product_name,
            store,
        ),
    )

    result = cursor.fetchone()
    return result and len(result) > 0 and result[0] == 1


def have_sent_at_least_one_target_live_notification_in_last_day(
    cursor: sqlite3.Cursor, product_name: str, store: str
):
    # return 1 if there has been at least 1 target live notification sent for the product in
    # the last 24 hours
    sql = """
    --begin-sql
        SELECT 1
        FROM notifications
        WHERE product_name = ?
            AND store = ?
            AND type = 'TARGET_LIVE'
            AND timestamp_sent BETWEEN datetime(current_timestamp, '-24 hours', 'localtime') AND datetime(current_timestamp, 'localtime')
        GROUP BY product_name
        HAVING count(*) > 0
        LIMIT 1
    --end-sql
    """

    cursor.execute(
        sql,
        (
            product_name,
            store,
        ),
    )

    result = cursor.fetchone()
    return result and len(result) > 0 and result[0] == 1


def should_send_target_live_notification(
    cursor: sqlite3.Cursor, product_name: str, store: str
):
    if has_been_at_least_2_target_live_records_in_last_day(cursor, product_name, store):
        return False

    if have_sent_at_least_one_target_live_notification_in_last_day(
        cursor, product_name, store
    ):
        return False

    return True


def has_been_at_least_one_successful_price_recording_in_last_day(
    cursor: sqlite3.Cursor, product_name: str, store: str
):
    # return 1 if there has been at least 1 successful price record of the product in
    # the last 24 hours
    sql = """
    --begin-sql
        SELECT 1
        FROM pricelog
        WHERE product_name = ?
            AND store = ?
            AND status != 'ERROR'
            AND timestamp_added BETWEEN datetime(current_timestamp, '-24 hours', 'localtime') AND datetime(current_timestamp, 'localtime')
        GROUP BY product_name
        HAVING count(*) > 0
        LIMIT 1
    --end-sql
    """

    cursor.execute(
        sql,
        (
            product_name,
            store,
        ),
    )

    result = cursor.fetchone()
    return result and len(result) > 0 and result[0] == 1


def has_been_at_least_one_successful_price_recording_in_last_week(
    cursor: sqlite3.Cursor, product_name: str, store: str
):
    # return 1 if there has been at least 1 successful price record of the product in
    # the last week
    sql = """
    --begin-sql
        SELECT 1
        FROM pricelog
        WHERE product_name = ?
            AND store = ?
            AND status != 'ERROR'
            AND timestamp_added BETWEEN datetime(current_timestamp, '-7 days', 'localtime') AND datetime(current_timestamp, 'localtime')
        GROUP BY product_name
        HAVING count(*) > 0
        LIMIT 1
    --end-sql
    """

    cursor.execute(
        sql,
        (
            product_name,
            store,
        ),
    )

    result = cursor.fetchone()
    return result and len(result) > 0 and result[0] == 1


def have_sent_at_least_one_error_notification_in_last_day(
    cursor: sqlite3.Cursor, product_name: str, store: str
):
    # return 1 if there has been at least 1 error notification sent for the product in
    # the last 24 hours
    sql = """
    --begin-sql
        SELECT 1
        FROM notifications
        WHERE product_name = ?
            AND store = ?
            AND type = 'ERROR'
            AND timestamp_sent BETWEEN datetime(current_timestamp, '-24 hours', 'localtime') AND datetime(current_timestamp, 'localtime')
        GROUP BY product_name
        HAVING count(*) > 0
        LIMIT 1
    --end-sql
    """

    cursor.execute(
        sql,
        (
            product_name,
            store,
        ),
    )

    result = cursor.fetchone()
    return result and len(result) > 0 and result[0] == 1


def have_sent_at_least_one_error_notification_in_last_week(
    cursor: sqlite3.Cursor, product_name: str, store: str
):
    # return 1 if there has been at least 1 error notification sent for the product in
    # the last week
    sql = """
    --begin-sql
        SELECT 1
        FROM notifications
        WHERE product_name = ?
            AND store = ?
            AND type = 'ERROR'
            AND timestamp_sent BETWEEN datetime(current_timestamp, '-7 days', 'localtime') AND datetime(current_timestamp, 'localtime')
        GROUP BY product_name
        HAVING count(*) > 0
        LIMIT 1
    --end-sql
    """

    cursor.execute(
        sql,
        (
            product_name,
            store,
        ),
    )

    result = cursor.fetchone()
    return result and len(result) > 0 and result[0] == 1


def should_send_error_notification(
    cursor: sqlite3.Cursor, product_name: str, store: str
):
    # this function should only be called if there is a current error condition on the product

    if has_been_at_least_one_successful_price_recording_in_last_week(
        cursor, product_name, store
    ):
        return False

    if have_sent_at_least_one_error_notification_in_last_week(
        cursor, product_name, store
    ):
        return False

    return True

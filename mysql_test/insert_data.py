import random
import string

import mysql.connector
from mysql.connector import Error


def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_number(length):
    return ''.join(random.choices(string.digits, k=length))


def random_line_name():
    return f"line-{random.randint(1, 10)}"


def random_station_name():
    return f"station-{random.randint(1, 20)}"


def insert_data(connection):
    for _ in range(100):  # Insert 100 rows of data into each table
        # Insert data into t98_line10_cq_station_up_down_qtty_date_st_hive
        query1 = f"""
        INSERT INTO t98_line10_cq_station_up_down_qtty_date_st_hive (
            line_name, station_name, stat_dt, up_train_on_psg, up_train_off_psg,
            down_train_on_psg, down_train_off_psg
        ) VALUES (
            'line1', 'station1', '01-01',
            '1', '2', '3','4'
        );
        """
        execute_query(connection, query1)

        # # Insert data into t98_daxing_station_up_down_qtty_date_st
        # query2 = f"""
        # INSERT INTO t98_daxing_station_up_down_qtty_date_st (
        #     line_name, station_name, stat_dt, up_train_on_psg, up_train_off_psg,
        #     down_train_on_psg, down_train_off_psg
        # ) VALUES (
        #     '{generate_random_string(10)}', '{generate_random_string(10)}', '{generate_random_string(10)}',
        #     '{generate_random_string(10)}', '{generate_random_string(10)}', '{generate_random_number(10)}',
        #     '{generate_random_number(10)}'
        # );
        # """
        # execute_query(connection, query2)
        #
        # # Insert data into t98_daxing_pasgr_hour_st_hive
        # query3 = f"""
        # INSERT INTO t98_daxing_pasgr_hour_st_hive (
        #     line_name, station_name, stat_dt, start_time, time_quantum,
        #     in_station_flow, out_station_flow
        # ) VALUES (
        #     '{generate_random_string(10)}', '{generate_random_string(10)}', '{generate_random_string(10)}',
        #     '{generate_random_string(8)}', '{generate_random_string(2)}', '{generate_random_number(10)}',
        #     '{generate_random_number(10)}'
        # );
        # """
        # execute_query(connection, query3)


def main():
    connection = create_connection("172.30.224.27", "root", "Cloudsea1!", "test_data_extraction")
    insert_data(connection)


if __name__ == "__main__":
    main()

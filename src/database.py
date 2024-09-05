import mysql.connector
from mysql.connector import Error
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
import logging
from config import setup_logging

setup_logging()

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            passwd=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset='utf8mb4',
            collation='utf8mb4_general_ci'
        )
        logging.info("MariaDB 데이터베이스 연결 성공")
    except Error as e:
        logging.error(f"데이터베이스 연결 오류: {e}")
    return connection

def get_all_sentences():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    phone_calls = []

    try:
        query = """
        SELECT JSON_UNQUOTE(JSON_EXTRACT(call_data, '$.phone_number')) as phone_number,
               JSON_UNQUOTE(JSON_EXTRACT(call_data, '$.sentence')) as sentence,
               JSON_EXTRACT(call_data, '$.iscall_start') as iscall_start,
               JSON_EXTRACT(call_data, '$.iscall_end') as iscall_end
        FROM PhoneCalls
        ORDER BY id
        """
        cursor.execute(query)
        results = cursor.fetchall()

        current_call = []
        for row in results:
            phone_number = row[0]
            sentence = row[1]
            iscall_start = row[2] == 'true'
            iscall_end = row[3] == 'true'

            if iscall_start:
                # 새로운 통화 시작
                if current_call:
                    phone_calls.append(current_call)
                current_call = [(phone_number, sentence)]

            else:
                current_call.append((phone_number, sentence))

            if iscall_end:
                # 통화 종료 시 통화 내용을 저장
                phone_calls.append(current_call)
                current_call = []

        # 마지막으로 남은 통화가 있으면 추가
        if current_call:
            phone_calls.append(current_call)

        return phone_calls

    except Error as e:
        logging.error(f"문장 조회 오류: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            logging.info("MySQL 연결이 닫혔습니다.")
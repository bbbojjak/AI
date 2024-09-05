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

def create_tables():
    connection = create_connection()
    if connection is None:
        return

    cursor = connection.cursor()

    # PhoneCalls 테이블 생성
    create_phone_calls_table = """
    CREATE TABLE IF NOT EXISTS PhoneCalls (
        id INT AUTO_INCREMENT PRIMARY KEY,
        call_data JSON,
        CONSTRAINT check_call_data CHECK (
            JSON_VALID(call_data) AND
            JSON_TYPE(JSON_EXTRACT(call_data, '$.phone_number')) = 'STRING' AND
            JSON_TYPE(JSON_EXTRACT(call_data, '$.sentence')) = 'STRING' AND
            JSON_TYPE(JSON_EXTRACT(call_data, '$.iscall_start')) = 'BOOLEAN' AND
            JSON_TYPE(JSON_EXTRACT(call_data, '$.iscall_end')) = 'BOOLEAN'
        )
    );
    """

    try:
        cursor.execute(create_phone_calls_table)
        connection.commit()
        logging.info("PhoneCalls 테이블이 생성되었습니다 (이미 존재할 경우 제외).")
    except Error as e:
        logging.error(f"테이블 생성 오류: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            logging.info("MySQL 연결이 닫혔습니다.")

def get_all_sentences():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    sentences = []

    try:
        query = "SELECT JSON_EXTRACT(call_data, '$.sentence') FROM PhoneCalls"
        cursor.execute(query)
        results = cursor.fetchall()
        
        for row in results:
            sentences.append(row[0])
        
        logging.info(f"{len(sentences)}개의 문장을 가져왔습니다.")
        return sentences
    except Error as e:
        logging.error(f"문장 조회 오류: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            logging.info("MySQL 연결이 닫혔습니다.")
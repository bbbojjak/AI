from sqlalchemy import create_engine, Column, Integer, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from config import DATABASE_URL, setup_logging
import logging

setup_logging()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PhoneCall(Base):
    __tablename__ = "PhoneCalls"

    id = Column(Integer, primary_key=True, index=True)
    call_data = Column(JSON)

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("테이블이 성공적으로 생성되었습니다.")
    except SQLAlchemyError as e:
        logging.error(f"테이블 생성 중 오류 발생: {e}")

def get_all_sentences():
    phone_calls = []
    current_call = []

    try:
        with SessionLocal() as session:
            query = text("""
                SELECT JSON_UNQUOTE(JSON_EXTRACT(call_data, '$.phone_number')) as phone_number,
                        JSON_UNQUOTE(JSON_EXTRACT(call_data, '$.sentence')) as sentence,
                        JSON_EXTRACT(call_data, '$.iscall_start') as iscall_start,
                        JSON_EXTRACT(call_data, '$.iscall_end') as iscall_end
                FROM PhoneCalls
                ORDER BY id
            """)
            
            result = session.execute(query)
            
            for row in result:
                phone_number, sentence, iscall_start, iscall_end = row

                if iscall_start == 'true':
                    if current_call:
                        phone_calls.append(current_call)
                    current_call = [(phone_number, sentence)]
                else:
                    current_call.append((phone_number, sentence))

                if iscall_end == 'true':
                    phone_calls.append(current_call)
                    current_call = []

            if current_call:
                phone_calls.append(current_call)

        logging.info(f"{len(phone_calls)}개의 통화 데이터를 가져왔습니다.")
        return phone_calls

    except SQLAlchemyError as e:
        logging.error(f"통화 데이터 조회 중 오류 발생: {e}")
        return []

if __name__ == "__main__":
    print(get_all_sentences())

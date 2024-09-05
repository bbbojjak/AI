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
    sentences = []
    try:
        with SessionLocal() as session:
            query = text("SELECT JSON_EXTRACT(call_data, '$.sentence') FROM PhoneCalls")
            result = session.execute(query)
            sentences = [row[0] for row in result]
        logging.info(f"{len(sentences)}개의 문장을 가져왔습니다.")
    except SQLAlchemyError as e:
        logging.error(f"문장 조회 중 오류 발생: {e}")
    return sentences

if __name__ == "__main__":
    create_tables()
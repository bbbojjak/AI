import logging
from dotenv import load_dotenv
import os
import json
import time

# .env 파일 로드
load_dotenv()

# 로그 설정
LOG_FILE = os.getenv("LOG_FILE", 'ai_voice_phishing.log')

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # 로그 파일에 구분선 추가
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write("\n" + "=" * 50 + "\n")
        f.write(f"New scraping session started at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n")

# DB 설정
MYSQL_HOST = os.getenv("DB_HOST", "%")
MYSQL_PORT = int(os.getenv("DB_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
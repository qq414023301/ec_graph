from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

#1. 目录路径

ROOT_DIR = Path(__file__).parent.parent.parent

DATA_DIR = ROOT_DIR / "data"
NER_DIR = "ner"
RAW_DATA_DIR = DATA_DIR / NER_DIR /"raw"
PROCESSED_DATA_DIR = DATA_DIR / NER_DIR / "processed"

LOG_DIR = ROOT_DIR / "logs"
CHECKPOINT_DIR = ROOT_DIR / "checkpoints"

#2. 数据文件名 和 模型名称
RAW_DATA_FILE = str(RAW_DATA_DIR / 'data.json')
MODEL_NAME = 'google-bert/bert-base-chinese'

#3. 超参数
BATCH_SIZE = 8
EPOCHS = 5
LEARNING_RATE = 1e-5

SAVE_STEPS = 20

#4. ner任务分类标签
LABELS = ['B','I','O']

#5. 数据库链接
MySQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": os.getenv('MYSQL_PASSWORD'),
    'database': 'gmall',
    'port': 3306,
}

Neo4j_CONFIG = {
    'uri':"neo4j://localhost:7687",
    'auth': ("neo4j",os.getenv('NEO4J'))
}

#web目录
WEB_STATIC_DIR = ROOT_DIR / 'src'/'web'/'static'
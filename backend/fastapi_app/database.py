# MongoDB 데이터베이스 연결 설정 파일
from pymongo import MongoClient

class Database:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client.my_database

    def get_collection(self, name):
        return self.db[name]

db = Database()

import logging
from sqlalchemy import create_engine,MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
import pymongo

class Store:
    database: str

    def __init__(self, db_path):
        self.engine = create_engine('postgresql://postgres:40960032@127.0.0.1:5432/bookstore') #本地服务器
        #self.engine = create_engine('postgresql+psycopg2://postgres:Tangqiong123@localhost/bookstore') #本地服务器
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.init_tables()

    def init_tables(self):
        try:
            conn = self.get_db_conn()
            conn.execute(
                "CREATE TABLE IF NOT EXISTS users ("
                "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
                "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS user_store("
                "user_id TEXT, store_id TEXT , PRIMARY KEY(store_id));"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS store( "
                "store_id TEXT, book_id TEXT, stock_level INTEGER, price INTEGER,"
                " PRIMARY KEY(store_id, book_id))"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS new_order( "
                "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT, "
                "status INTEGER DEFAULT 1, total_price INTEGER, order_time INTEGER )"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS new_order_detail( "
                "order_id TEXT, book_id TEXT, count INTEGER,  "
                "PRIMARY KEY(order_id, book_id))"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS invert_index( "
                "search_key TEXT, search_id serial, book_id TEXT, "
                "book_title TEXT, book_author TEXT, "
                "PRIMARY KEY(search_key, search_id))"
            )

            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS old_order( "
            #     "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT, "
            #     "status INTEGER, total_price INTEGER, order_time INTEGER )"
            # )
            #
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS old_order_detail( "
            #     "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
            #     "PRIMARY KEY(order_id, book_id))"
            # )

            conn.commit()
        except SQLAlchemyError as e:
            logging.error(e)
            conn.rollback()

    def get_db_conn(self):
        self.Base = declarative_base()
        self.metadata = MetaData()
        self.DBSession = sessionmaker(bind=self.engine)
        self.conn = self.DBSession()
        return self.conn

    def get_db_mongo(self):
        self.mongodb = self.client["bookstore"]
        # mongodb目前需手动建立文档集
        return self.mongodb


database_instance: Store = None


def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()

def get_db_mongo():
    global database_instance
    return database_instance.get_db_mongo()
from be.model import error
from be.model import db_conn
import json
from sqlalchemy.exc import SQLAlchemyError
from pymongo.errors import PyMongoError
from be.model import nlp
from be.model.nlp import *


class Seller(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(self, user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            response = self.mongo['book'].find_one({'id':book_id})
            book_info_json = json.loads(book_json_str)
            price = book_info_json.get("price")
            book_info_json.pop("price")

            if response != None:
                mongo_id = str(response["_id"])
            else:
                # ---分离作者国籍开始---
                # 将作者栏中的作者国籍拆出，便于建立倒排表
                author = None
                if "author" in book_info_json.keys():
                    author = book_info_json.get("author")
                    country, author = get_country_and_author(author)
                    if country != "" and author != "":
                        book_info_json["country"] = country
                        book_info_json["author"] = author
                # ---分离作者国籍结束---

                # ---提取关键字开始---
                # 提取简介及目录中关键字，并将关键字加入书的标签
                tags = []
                if "tags" in book_info_json.keys():
                    tags = book_info_json.get("tags")
                if "author_intro" in book_info_json.keys():
                    keyword = nlp.get_keyword(book_info_json.get("author_intro"))
                    tags += keyword
                if "book_intro" in book_info_json.keys():
                    keyword = nlp.get_keyword(book_info_json.get("book_intro"))
                    tags += keyword
                if "content" in book_info_json.keys():
                    keyword = nlp.get_keyword(book_info_json.get("content"))
                    tags += keyword
                tags = list(set(tags))
                book_info_json["tags"] = tags
                # ---提取关键字结束---

                # ---加入倒排索引开始---
                # 将新书的标题、作者、标签加入倒排索引表
                preffixs = []
                title = book_info_json.get("title")
                preffixs += nlp.get_middle_ffix(title)
                if "author" in book_info_json.keys():
                    names = parse_name(book_info_json.get("author"))
                    for i in range(1,len(names)):
                        preffixs += nlp.get_preffix(names[i])
                    preffixs += nlp.get_preffix(book_info_json.get("author"))
                if "original_title" in book_info_json.keys():
                    preffixs += nlp.get_preffix(book_info_json.get("original_title"))
                if "translator" in book_info_json.keys():
                    names = parse_name(book_info_json.get("translator"))
                    for i in range(1, len(names)):
                        preffixs += nlp.get_preffix(names[i])
                    preffixs += nlp.get_preffix(book_info_json.get("translator"))
                preffixs = list(set(preffixs))
                for preffix in preffixs:
                    self.conn.execute(
                        "INSERT into invert_index(search_key, book_id, book_title, book_author) "
                        "VALUES (:sky, :bid, :til, :asr)",
                        {'sky': preffix, 'bid': book_id, 'til': title, 'asr': author})
                # ---加入倒排索引结束---

                response = self.mongo['book'].insert_one(book_info_json)
                mongo_id = str(response.inserted_id)

            self.conn.execute(
                "INSERT into store(store_id, book_id, stock_level, price) VALUES (:sid, :bid, :skl, :prc)",
                {'sid': store_id, 'bid': book_id, 'skl': stock_level, 'prc': price})
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except PyMongoError as e:
            return 529, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            self.conn.execute("UPDATE store SET stock_level = stock_level + :asl  WHERE store_id = :sid AND book_id = :bid",
                              {'asl':add_stock_level, 'sid':store_id, 'bid':book_id})
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            self.conn.execute("INSERT into user_store(store_id, user_id) VALUES (:sid, :uid)", {'sid':store_id, 'uid':user_id})
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    # 卖家发货
    def send_books(self,store_id,order_id):
        try:
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.order_id_exist(order_id):   #增加order_id不存在的错误处理
                return error.error_invalid_order_id(order_id)
            cursor = self.conn.execute(
                "SELECT status FROM new_order where order_id = '%s' ;" % (order_id))
            row = cursor.fetchone()
            status = row[0]
            if status != 2:
                return error.error_invalid_order_status(order_id)

            self.conn.execute(
                "UPDATE new_order set status=3 where order_id = '%s' ;" % (order_id))
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def store_processing_order(self, seller_id):
        try:
            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            result = []
            cursor = self.conn.execute(
                "SELECT o.order_id, o.store_id, o.status, o.total_price, o.order_time "
                "FROM new_order o, user_store s "
                "WHERE s.user_id = :user_id AND s.store_id = o.store_id ",
                {"user_id": seller_id, })
            if cursor.rowcount != 0:
                rows = cursor.fetchall()
                for row in rows:
                    order = {
                        "order_id": row[0],
                        "store_id": row[1],
                        "status": row[2],
                        "total_price": row[3],  # 总价
                        "order_time": row[4]  # 时间戳，改成时间
                    }
                    books = []
                    cursor = self.conn.execute(
                        "SELECT book_id, count FROM new_order_detail WHERE order_id = :order_id ",
                        {"order_id": order["order_id"], })
                    bookrows = cursor.fetchall()
                    for bookrow in bookrows:
                        book = {
                            "book_id": bookrow[0],
                            "count": bookrow[1]
                        }
                        books.append(book)
                    order["books"] = books
                    result.append(order)
            else:
                result = ["NO Processing Order"]
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e)), []
        except BaseException as e:
            return 530, "{}".format(str(e)), []
        return 200, "ok", result

    def store_history_order(self, store_id):
        try:
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)

            result = []
            orders = self.mongo['history_order'].find({'store_id': store_id}, {'_id': 0})
            for order in orders:
                result.append(order)

        except PyMongoError as e:
            return 529, "{}".format(str(e)), []
        except BaseException as e:
            return 530, "{}".format(str(e)), []
        return 200, "ok", result

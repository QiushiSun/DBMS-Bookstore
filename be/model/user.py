import jwt
import time
import logging
from be.model import error
from be.model import db_conn
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pymongo.errors import PyMongoError
from be.model.nlp import encrypt

# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.decode("utf-8")


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:# 判断登录信息是否失效
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            password = encrypt(password)
            self.conn.execute(
                "INSERT into users(user_id, password, balance, token, terminal) "
                "VALUES (:uid, :pw, 0, :tok, :ter);",
                { "uid":user_id,"pw": password,"tok":token,"ter":terminal })
            self.conn.commit()
        except IntegrityError:
            return error.error_exist_user_id(user_id)
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        cursor = self.conn.execute("SELECT token from users where user_id= :uid", {"uid":user_id})
        row = cursor.fetchone()
        if row is None:
            return error.error_authorization_fail()
        db_token = row[0]
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):#检查密码
        cursor = self.conn.execute("SELECT password from users where user_id= :uid", {"uid":user_id})
        row = cursor.fetchone()
        if row is None:
            return error.error_authorization_fail()

        if encrypt(password) != row[0]:
            return error.error_authorization_fail()

        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)#登录时先检查密码，可改为登录检查
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            cursor = self.conn.execute(
                "UPDATE users set token= :tok , terminal = :ter where user_id = :uid",
                {'tok':token, 'ter':terminal, 'uid':user_id})
            if cursor.rowcount == 0:
                return error.error_authorization_fail() + ("", )
            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        try:
            code, message = self.check_token(user_id, token)#可改为登出检查
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)
            cursor = self.conn.execute(
                "UPDATE users SET token = :tok, terminal = :ter WHERE user_id= :uid",
                {'tok':dummy_token, 'ter':terminal, 'uid':user_id})
            if cursor.rowcount == 0:
                return error.error_authorization_fail()

            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)#注销操作前检查密码
            if code != 200:
                return code, message

            cursor = self.conn.execute("DELETE from users where user_id= :uid", {'uid':user_id})
            if cursor.rowcount == 1:
                self.conn.commit()
            else:
                return error.error_authorization_fail()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            new_password = encrypt(new_password)
            cursor = self.conn.execute(
                "UPDATE users set password = :pw, token= :tok, terminal = :ter where user_id = :uid",
                {'pw':new_password, 'tok':token, 'ter':terminal, 'uid':user_id})
            if cursor.rowcount == 0:
                return error.error_authorization_fail()

            self.conn.commit()
        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def processing_order(self, user_id):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)

            result = []
            cursor = self.conn.execute(
                "SELECT order_id, store_id, status, total_price, order_time FROM new_order WHERE user_id = :user_id ",
                {"user_id": user_id, })
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

    def history_order(self, user_id):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)

            result = []
            orders = self.mongo['history_order'].find({'user_id': user_id},{'_id':0})
            for order in orders:
                result.append(order)

        except PyMongoError as e:
            return 529, "{}".format(str(e)), []
        except BaseException as e:
            return 530, "{}".format(str(e)), []
        return 200, "ok", result

    def recommend(self, user_id):
        try:
            code, message, orders = self.history_order(user_id)
            if code != 200:
                return error.error_non_exist_user_id(user_id)

            reco = {}
            labels = []
            for order in orders:
                boughtbooks = order['books']
                for boughtbook in boughtbooks:
                    eachbook = self.mongo['book'].find_one({'id': boughtbook['book_id']},
                                                           {'_id': 0, 'id': 1, 'title': 1, 'author': 1, 'tags': 1, 'publisher':1})
                    labels += eachbook['tags']
                    reco[eachbook['id']] = eachbook
                    reco[eachbook['id']]['tags'] = []
                    books = self.mongo['book'].find({'$or': [{'author': eachbook['author']},
                                                             {'publisher': eachbook['publisher']},
                                                             {'tags': {'$elemMatch': {'$in': eachbook['tags']}}}]},
                                                    {'_id': 0, 'id': 1, 'title': 1, 'author': 1, 'tags': 1})
                    for book in books:
                        if book['id'] not in reco.keys():
                            reco[book['id']] = book
            labels = list(set(labels))
            for book in reco.values():
                book['sim'] = jarcard_sim(labels, book['tags'])
                book.pop('tags')
            result = sorted(reco.values(), key=lambda k:k['sim'], reverse=True)
            result = result[:5]
        except PyMongoError as e:
            return 529, "{}".format(str(e)), []
        except BaseException as e:
            return 530, "{}".format(str(e)), []
        return 200, "ok", result


def jarcard_sim(a, b):
    i = set(a).intersection(set(b))
    u = set(a + b)
    if len(u) == 0:
        return 0
    return len(i)/len(u)


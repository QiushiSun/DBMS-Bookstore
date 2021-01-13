from be.model import store


class DBConn:
    def __init__(self):
        self.conn = store.get_db_conn()
        self.mongo = store.get_db_mongo()

    def user_id_exist(self, user_id):
        cursor = self.conn.execute("SELECT user_id FROM users WHERE user_id = :uid;", {'uid':user_id})
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        cursor = self.conn.execute("SELECT book_id FROM store WHERE store_id = :sid AND book_id = :bid;", {'sid':store_id, 'bid':book_id})
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        cursor = self.conn.execute("SELECT store_id FROM user_store WHERE store_id = :sid;", {'sid':store_id})
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def order_id_exist(self, order_id):
        cursor = self.conn.execute("SELECT order_id FROM new_order WHERE order_id = :oid;", {'oid':order_id})
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True
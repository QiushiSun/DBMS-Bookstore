import random
from fe.access import book
from fe.access.new_seller import register_new_seller


class GenBook:
    def __init__(self, user_id, store_id):
        self.user_id = user_id
        self.store_id = store_id
        self.password = self.user_id
        self.seller = register_new_seller(self.user_id, self.password)
        code = self.seller.create_store(store_id)
        assert code == 200
        self.__init_book_list__()

    def __init_book_list__(self):
        self.buy_book_info_list = []
        self.buy_book_id_list = []

    def gen(self, non_exist_book_id: bool, low_stock_level, max_book_count: int = 100) -> (bool, []):
        self.__init_book_list__()
        ok = True
        book_db = book.BookDB()
        rows = book_db.get_book_count()
        start = 0
        if rows > max_book_count:
            start = random.randint(0, rows - max_book_count)
        size = random.randint(1, max_book_count)
        books = book_db.get_book_info(start, size)
        book_id_exist = []
        book_id_stock_level = {}
        for bk in books:
            if low_stock_level:
                stock_level = random.randint(0, 100)
            else:
                stock_level = random.randint(2, 100)
            code = self.seller.add_book(self.store_id, stock_level, bk)
            assert code == 200
            book_id_stock_level[bk.id] = stock_level
            book_id_exist.append(bk)

        for bk in book_id_exist:
            stock_level = book_id_stock_level[bk.id]
            if stock_level > 1:
                buy_num = random.randint(1, stock_level)
            else:
                buy_num = 0
            # add a new pair
            if non_exist_book_id:
                bk.id = bk.id + "_x"
            if low_stock_level:
                buy_num = stock_level + 1
            self.buy_book_info_list.append((bk, buy_num))

        for item in self.buy_book_info_list:
            self.buy_book_id_list.append((item[0].id, item[1]))
        return ok, self.buy_book_id_list

    def get_seller(self):
        return self.seller

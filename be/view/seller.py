from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import seller
import json

bp_seller = Blueprint("seller", __name__, url_prefix="/seller")


@bp_seller.route("/create_store", methods=["POST"])
def seller_create_store():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    s = seller.Seller()
    code, message = s.create_store(user_id, store_id)
    return jsonify({"message": message}), code


@bp_seller.route("/add_book", methods=["POST"])
def seller_add_book():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    book_info: str = request.json.get("book_info")
    stock_level: str = request.json.get("stock_level", 0)

    s = seller.Seller()
    code, message = s.add_book(user_id, store_id, book_info.get("id"), json.dumps(book_info), stock_level)

    return jsonify({"message": message}), code


@bp_seller.route("/add_stock_level", methods=["POST"])
def add_stock_level():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    book_id: str = request.json.get("book_id")
    add_num: str = request.json.get("add_stock_level", 0)

    s = seller.Seller()
    code, message = s.add_stock_level(user_id, store_id, book_id, add_num)

    return jsonify({"message": message}), code

# 发货
@bp_seller.route("/send_books", methods=["POST"])
def send_books():
    store_id: str = request.json.get("store_id")
    order_id: str = request.json.get("order_id")

    s = seller.Seller()
    code, message = s.send_books(store_id, order_id)

    return jsonify({"message": message}), code

@bp_seller.route("/store_processing_order", methods=["POST"])
def check_store_processing_orders():
    seller_id = request.json.get("seller_id", "")
    s = seller.Seller()
    code, message, result = s.store_processing_order(seller_id)
    return jsonify({"message": message, "result": result}), code

@bp_seller.route("/store_history_order", methods=["POST"])
def check_store_history_orders():
    store_id = request.json.get("store_id", "")
    s = seller.Seller()
    code, message, result = s.store_history_order(store_id)
    return jsonify({"message": message, "result": result}), code
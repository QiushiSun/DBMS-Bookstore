import logging
from flask import request
from be.view import auth
from be.view import seller
from be.view import buyer
from be.model.store import init_database
from flask import Blueprint
import os
from flask import Flask
from flask_apscheduler import APScheduler
import be.tasks

bp_shutdown = Blueprint("shutdown", __name__)


def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


@bp_shutdown.route("/shutdown")
def be_shutdown():
    shutdown_server()
    return "Server shutting down..."


def be_run(auto_cancel=False):
    this_path = os.path.dirname(__file__)
    parent_path = os.path.dirname(this_path)
    log_file = os.path.join(parent_path, "app.log")
    init_database(parent_path)

    logging.basicConfig(filename=log_file, level=logging.ERROR)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

    app = Flask(__name__)
    app.register_blueprint(bp_shutdown)
    app.register_blueprint(auth.bp_auth)
    app.register_blueprint(seller.bp_seller)
    app.register_blueprint(buyer.bp_buyer)

    if auto_cancel == True:
        sched = APScheduler()
        app.config.from_object(be.tasks.Config())
        sched.init_app(app)
        sched.start()
        print("Settings: Auto Cancel Out Of Time Orders")
    app.run()


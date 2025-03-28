# Copyright 2025 Intent Exchange, Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the “Software”), to deal in the Software without
# restriction, including without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import sys
import os
import logging
from flask import (
    Flask,
    has_request_context,
    request,

)
from flask_restx import Api
from flask_cors import CORS
# from flask_migrate import Migrate
from flask.logging import default_handler

sys.path.append(os.path.join(os.path.dirname(__file__), "."))
from config import ConfigIns
from database import db, ma

LOGFILE_NAME = "/log/debug.log"
MH_SYS_VERSION = "1.0.0"

app = Flask(__name__)
CORS(app)

# SWAGGER設定
app.config["RESTX_MASK_SWAGGER"] = False
api = Api(
    app,
    version=MH_SYS_VERSION,
    title="Mobility Hub Manegement System API",
    description="モビリティハブ用API",
)
# DB 設定
# Migrate(app, db)
app.config.from_object("config.Config")
db.init_app(app)
ma.init_app(app)

import model.devanning_plan
import model.vanning_plan

with app.app_context():
    db.create_all()


# ログ設定
app.logger.setLevel(logging.DEBUG)
log_handler = logging.FileHandler(ConfigIns.LOGFILE_NAME)
log_handler.setLevel(logging.DEBUG)


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)


formatter = RequestFormatter("[%(asctime)s] %(levelname)s : %(module)s: %(message)s")

default_handler.setFormatter(formatter)
log_handler.setFormatter(formatter)
app.logger.addHandler(log_handler)
app.logger.info(f"自動運転支援道：Mobilty Hub管理システム({MH_SYS_VERSION}) サーバー起動")


# 各API登録
from mh_api import mh_api_blueprint

app.register_blueprint(mh_api_blueprint, url_prefix="/mhapi/v1")


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response


@app.teardown_appcontext
def shutdown_session(exception=None):
    # リクエスト単位のセッションの終了時の処理があれば
    pass


@app.route("/healthcheck")
def healthcheck():
    return "healthcheck OK"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)

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

from flask import Blueprint
from flask_restx import Api
import os
import logging
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import ConfigIns

logger = logging.getLogger("app.flask")
logger.setLevel(logging.getLevelNamesMapping()[os.environ.get("LOGLEVEL", "DEBUG")])
log_handler = logging.FileHandler(ConfigIns.LOGFILE_NAME)
log_handler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)s : %(module)s: %(message)s")
)
logger.addHandler(log_handler)

mh_api_blueprint = Blueprint("mh_api", __name__)
mh_api = Api(
    mh_api_blueprint,
    title="Mobility Hub Manegement System API",
    version="1.1.1",
    description=(
        "<h2>共同輸送システム モビリティハブ管理システム API</h2>"
        "<h3>改版履歴</h3>"
        "<ul>"
        "  <li>0.9.0 : 2025/01/17</li>"
        "    <ul>初版作成</ul>"
        "  </li>"
        "  <li>1.0.0 : 2025/01/21</li>"
        "    <ul>MH作業実績時間を追加</ul>"
        "  </li>"
        "  <li>1.1.0 : 2025/02/04</li>"
        "    <ul>発MHのフラグ（is_departure_mh）を追加</ul>"
        "  </li>"
        "  <li>1.1.1 : 2025/02/14</li>"
        "    <ul>バンニング、デバンニングの検索APIを追加</ul>"
        "  </li>"
        "<ul>"
    ),
    doc="/swagger/",
)

from .vanning_plan_api import vanning_plan_api_ns
from .devanning_plan_api import devanning_plan_api_ns
from .plan_search_api import plan_search_api_ns

mh_api.add_namespace(vanning_plan_api_ns, path="/vanning_plan")
mh_api.add_namespace(devanning_plan_api_ns, path="/devanning_plan")
mh_api.add_namespace(plan_search_api_ns, path="/plan_search")

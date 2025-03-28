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
from flask import request
from flask_restx import Namespace, Resource

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from model.devanning_plan import DevanningPlanModel, DevanningPlanModelSchema
from model.vanning_plan import VanningPlanModel, VanningPlanModelSchema
from database import db, ma

logger = logging.getLogger("app.flask")
logger.setLevel(logging.getLevelNamesMapping()[os.environ.get("LOGLEVEL", "DEBUG")])


plan_search_api_ns = Namespace(
    "/mhapi/v1/plan_search", description="バンニング・デバンニング計画検索"
)



@plan_search_api_ns.route("/")
class PlanSearchApi(Resource):


    @plan_search_api_ns.doc(
        description=("バンニング・デバンニング計画検索 <br/>"),
        params={
            "is_departure_mh": "発MHなら1、着MHなら0(required)",
            "trsp_instruction_id": "trsp_instruction_id(required)",
            "is_vanning": "バンニング計画なら1、デバンニング計画なら0(required)"
        },
    )
    def get(self):
        logger.debug("バンニング・デバンニング計画検索")
        try:
            query_params = request.args.to_dict()
            is_departure_mh = int(query_params.get("is_departure_mh", 0))
            trsp_instruction_id = query_params.get("trsp_instruction_id")
            is_vanning = int(query_params.get("is_vanning", 0))
            if is_vanning == 1:
                vanning_plan = (
                    db.session.query(VanningPlanModel)
                    .filter(
                        VanningPlanModel.is_departure_mh == is_departure_mh,
                        VanningPlanModel.trsp_instruction_id == trsp_instruction_id,
                    )
                    .first()
                )
                if vanning_plan is None:
                    plan = None
                else:
                    vanning_plan_schema = VanningPlanModelSchema(many=False)
                    plan = vanning_plan_schema.dump(vanning_plan)
            else:
                devanning_plan = (
                    db.session.query(DevanningPlanModel)
                    .filter(
                        DevanningPlanModel.is_departure_mh == is_departure_mh,
                        DevanningPlanModel.trsp_instruction_id == trsp_instruction_id,
                    )
                    .first()
                )
                if devanning_plan is None:
                    plan = None
                else:
                    devanning_plan_schema = DevanningPlanModelSchema(many=False)
                    plan = devanning_plan_schema.dump(devanning_plan)
            if plan is None:
                result = {
                    "plan": None,
                    "result": False,
                    "error_msg": "Not Found",
                }
                status = 404
            else:
                status = 200
                result = {
                    "plan": plan,
                    "result": True,
                    "error_msg": "",
                }
            logger.debug(f"result:{result}")
        except Exception as e:
            logger.error(e, exc_info=True, stack_info=True)
            result = {"plan": {}, "result": False, "error_msg": "Error"}
            status = 400
        return result, status

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
import datetime
import dateutil.parser
from sqlalchemy import or_, and_
from flask import jsonify, request, make_response
from flask_restx import Namespace, Resource, fields

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from com.helper import (
    create_restx_model_usingSchema,
    create_response_model,
)
from model.vanning_plan import VanningPlanModel, VanningPlanModelSchema
from database import db, ma

logger = logging.getLogger("app.flask")
logger.setLevel(logging.getLevelNamesMapping()[os.environ.get("LOGLEVEL", "DEBUG")])


vanning_plan_api_ns = Namespace("/mhapi/v1/vanning_plan", description="バンニング計画")

post_request_model = create_restx_model_usingSchema(
    "VanningPlanBody",
    vanning_plan_api_ns,
    VanningPlanModelSchema,
    exclude_fields=["created_at", "updated_at"],
)


@vanning_plan_api_ns.route("/<string:mh>/<string:trsp_instruction_id>")
@vanning_plan_api_ns.param("mh", "MHのGLN")
@vanning_plan_api_ns.param("trsp_instruction_id", "trsp_instruction_id")
class VanningPlanAPI(Resource):

    post_response_model = create_response_model(
        "VanningPlanResult",
        vanning_plan_api_ns,
        "vanning_plan",
        post_request_model,
    )

    @vanning_plan_api_ns.doc(
        description=(
            "バンニング計画更新 <br/>"
            "- 共同輸送システム・コアからのみ利用可"
            "計画の変更または実績の登録に使用する。"
        ),
    )
    @vanning_plan_api_ns.expect(post_request_model)
    @vanning_plan_api_ns.marshal_with(post_response_model)
    def put(self, mh, trsp_instruction_id):
        logger.debug("バンニング計画更新")
        try:
            data = request.get_json(force=True)
            vanning_plan = (
                db.session.query(VanningPlanModel)
                .filter(
                    VanningPlanModel.mh == mh,
                    VanningPlanModel.trsp_instruction_id == trsp_instruction_id,
                )
                .first()
            )
            is_insert = False
            if vanning_plan is None:
                # insert
                vanning_plan = VanningPlanModel(
                    mh=mh,
                    trsp_instruction_id=trsp_instruction_id,
                )
                is_insert = True

            if "mh_space_list" in data:
                vanning_plan.mh_space_list_str = ",".join(data["mh_space_list"])
            if "shipper_cid" in data:
                vanning_plan.shipper_cid = data["shipper_cid"]
            if "recipient_cid" in data:
                vanning_plan.recipient_cid = data["recipient_cid"]
            if "carrier_cid" in data:
                vanning_plan.carrier_cid = data["carrier_cid"]
            if "tractor_giai" in data:
                vanning_plan.tractor_giai = data["tractor_giai"]
            if "trailer_giai_list" in data:
                vanning_plan.trailer_giai_list_str = ",".join(
                    data["trailer_giai_list"]
                )
            if "req_from_time" in data:
                if data["req_from_time"] != "" and data["req_from_time"] is not None:
                    vanning_plan.req_from_time = dateutil.parser.parse(data["req_from_time"])
            if "req_to_time" in data:
                if data["req_to_time"] != "" and data["req_to_time"] is not None:
                    vanning_plan.req_to_time = dateutil.parser.parse(data["req_to_time"])
            if "actual_time" in data:
                if data["actual_time"] != "" and data["actual_time"] is not None:
                    vanning_plan.actual_time = dateutil.parser.parse(data["actual_time"])
            if "status" in data:
                vanning_plan.status = data["status"]
            if "is_bl_need" in data:
                vanning_plan.is_bl_need = data["is_bl_need"]
            if "is_departure_mh" in data:
                vanning_plan.is_departure_mh = data["is_departure_mh"]
            dt = datetime.datetime.now()
            vanning_plan.updated_at = dt.isoformat()

            if is_insert:
                db.session.add(vanning_plan)
            db.session.commit()
            vanning_plan_schema = VanningPlanModelSchema(many=False)
            result = {
                "vanning_plan": vanning_plan_schema.dump(vanning_plan),
                "result": True,
                "error_msg": "",
            }
            logger.debug(f"result:{result}")
            status = 200
        except Exception as e:
            logger.error(e, exc_info=True, stack_info=True)
            db.session.rollback()
            result = {"vanning_plan": {}, "result": False, "error_msg": "Error"}
            status = 400
        return result, status

    @vanning_plan_api_ns.doc(
        description=(
            "バンニング計画登録 <br/>" "- 共同輸送システム・コアからのみ利用可"
        ),
    )
    @vanning_plan_api_ns.expect(post_request_model)
    @vanning_plan_api_ns.marshal_with(post_response_model)
    def post(self, mh, trsp_instruction_id):
        try:
            data = request.get_json(force=True)
            logger.debug(f"バンニング計画登録: {data}")
            vanning_plan = (
                db.session.query(VanningPlanModel)
                .filter(
                    VanningPlanModel.mh == mh,
                    VanningPlanModel.trsp_instruction_id == trsp_instruction_id,
                )
                .first()
            )
            dt = datetime.datetime.now()
            is_add = False
            if vanning_plan is None:
                vanning_plan = VanningPlanModel(
                    mh=mh,
                    trsp_instruction_id=trsp_instruction_id,
                )
                vanning_plan.created_at = dt.isoformat()
                is_add = True
            vanning_plan.updated_at = dt.isoformat()

            if "mh_space_list" in data:
                vanning_plan.mh_space_list_str = ",".join(data["mh_space_list"])
            if "shipper_cid" in data:
                vanning_plan.shipper_cid = data["shipper_cid"]
            if "recipient_cid" in data:
                vanning_plan.recipient_cid = data["recipient_cid"]
            if "carrier_cid" in data:
                vanning_plan.carrier_cid = data["carrier_cid"]
            if "tractor_giai" in data:
                vanning_plan.tractor_giai = data["tractor_giai"]
            if "trailer_giai_list" in data:
                vanning_plan.trailer_giai_list_str = ",".join(
                    data["trailer_giai_list"]
                )
            vanning_plan.req_from_time = None
            vanning_plan.req_to_time = None
            vanning_plan.actual_time = None
            if "req_from_time" in data:
                if data["req_from_time"] != "" and data["req_from_time"] is not None:
                    vanning_plan.req_from_time = dateutil.parser.parse(data["req_from_time"])
            if "req_to_time" in data:
                if data["req_to_time"] != "" and data["req_to_time"] is not None:
                    vanning_plan.req_to_time = dateutil.parser.parse(data["req_to_time"])
            if "status" in data:
                vanning_plan.status = data["status"]
            if "is_bl_need" in data:
                vanning_plan.is_bl_need = data["is_bl_need"]
            if "is_departure_mh" in data:
                vanning_plan.is_departure_mh = data["is_departure_mh"]

            if is_add:
                db.session.add(vanning_plan)
            db.session.commit()
            vanning_plan_schema = VanningPlanModelSchema(many=False)
            result = {
                "vanning_plan": vanning_plan_schema.dump(vanning_plan),
                "result": True,
                "error_msg": "",
            }
            logger.debug(f"result:{result}")
            status = 200
        except Exception as e:
            logger.error(e, exc_info=True, stack_info=True)
            db.session.rollback()
            result = {"vanning_plan": {}, "result": False, "error_msg": "Error"}
            status = 400
        return result, status

    @vanning_plan_api_ns.doc(
        description=("バンニング計画詳細取得 <br/>"),
    )
    @vanning_plan_api_ns.marshal_with(post_response_model)
    def get(self, mh, trsp_instruction_id):
        logger.debug(
            f"バンニング計画詳細取得 mh={mh} trsp_instruction_id={trsp_instruction_id}"
        )
        try:
            vanning_plan = (
                db.session.query(VanningPlanModel)
                .filter(
                    VanningPlanModel.mh == mh,
                    VanningPlanModel.trsp_instruction_id == trsp_instruction_id,
                )
                .first()
            )
            if vanning_plan is None:
                result = {
                    "vanning_plan": None,
                    "result": False,
                    "error_msg": "Not Found",
                }
            else:
                vanning_plan_schema = VanningPlanModelSchema(many=False)
                result = {
                    "vanning_plan": vanning_plan_schema.dump(vanning_plan),
                    "result": True,
                    "error_msg": "",
                }
            logger.debug(f"result:{result}")
            status = 200
        except Exception as e:
            logger.error(e, exc_info=True, stack_info=True)
            result = {"vanning_plan": {}, "result": False, "error_msg": "Error"}
            status = 400
        return result, status

    del_res_model = vanning_plan_api_ns.model(
        "DelResModel",
        {
            "result": fields.Boolean(example=True, description="API結果"),
            "error_msg": fields.String(example="", description="エラーメッセージ"),
        },
    )

    @vanning_plan_api_ns.doc(
        description=(
            "バンニング計画削除 <br/>" "- 共同輸送システム・コアからのみ利用可"
        ),
    )
    @vanning_plan_api_ns.marshal_with(del_res_model)
    def delete(self, mh, trsp_instruction_id):
        logger.debug("バンニング計画削除")
        try:
            vanning_plan = (
                db.session.query(VanningPlanModel)
                .filter(
                    VanningPlanModel.mh == mh,
                    VanningPlanModel.trsp_instruction_id == trsp_instruction_id,
                )
                .first()
            )
            if vanning_plan is None:
                result = {"result": False, "error_msg": "Not found"}
                return result, 403
            db.session.query(VanningPlanModel).filter(
                VanningPlanModel.mh == mh,
                VanningPlanModel.trsp_instruction_id == trsp_instruction_id,
            ).delete()
            result = {
                "result": True,
                "error_msg": "",
            }
            logger.debug(f"result:{result}")
            status = 200
        except Exception as e:
            logger.error(e, exc_info=True, stack_info=True)
            result = {"result": False, "error_msg": "Error"}
            status = 400
        return result, status


@vanning_plan_api_ns.route("/<string:mh>")
@vanning_plan_api_ns.param("mh", "MHのGLN")
class VanningPlanListAPI(Resource):
    get_list_res_model = create_response_model(
        "VanningPlanListResult",
        vanning_plan_api_ns,
        "vanning_plan_list",
        post_request_model,
        True,
    )

    @vanning_plan_api_ns.doc(
        description=("バンニング計画検索<br/>"),
    )
    @vanning_plan_api_ns.param("date", "検索する日付[yyyymmhh](required)")
    @vanning_plan_api_ns.marshal_with(get_list_res_model)
    def get(self, mh):
        logger.debug("バンニング計画検索")
        try:
            if request.args.get("date") is not None:
                date_str = request.args.get("date")
            else:
                logger.debug("dateがない")
                result = {
                    "vanning_plan_list": {},
                    "result": False,
                    "error_msg": "date is missing",
                }
                return result, 400
            start_time = datetime.datetime.strptime(date_str, "%Y%m%d")
            end_time = datetime.datetime.strptime(
                date_str, "%Y%m%d"
            ) + datetime.timedelta(days=1)
            vanning_plan = db.session.query(VanningPlanModel).filter(
                and_(
                    VanningPlanModel.mh == mh,
                    or_(
                        and_(
                            VanningPlanModel.req_from_time >= start_time,
                            VanningPlanModel.req_from_time < end_time,
                        ),
                        and_(
                            VanningPlanModel.req_to_time >= start_time,
                            VanningPlanModel.req_to_time < end_time,
                        ),
                    ),
                )
            )
            vanning_plan_schema = VanningPlanModelSchema(many=True)
            result = {
                "vanning_plan_list": vanning_plan_schema.dump(vanning_plan),
                "result": True,
                "error_msg": "",
            }
            logger.debug(f"result:{result}")
            status = 200
        except Exception as e:
            logger.error(e, exc_info=True, stack_info=True)
            result = {"vanning_plan_list": {}, "result": False, "error_msg": "Error"}
            status = 400
        return result, status

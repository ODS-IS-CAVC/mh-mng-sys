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

from datetime import datetime, date, time
from marshmallow import fields, validate, ValidationError
import sys
import os
from sqlalchemy.ext.hybrid import hybrid_property

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from database import db, ma


class DevanningPlanModel(db.Model):
    __tablename__ = "devanning_plan"
    id = db.Column(
        db.Integer, primary_key=True, doc="The unique id", autoincrement=True
    )  # created to have a primary key
    # GLNは１６桁
    mh = db.Column(db.String(16), nullable=False, doc="MHのGLN(3桁＋13桁)")
    mh_space_list_str = db.Column(
        db.String(256), nullable=False, doc="MHの駐車枠のリスト（カンマ区切りの文字列）"
    )
    shipper_cid = db.Column(db.String(50), nullable=True, doc="荷主の事業者ID")
    recipient_cid = db.Column(db.String(50), nullable=True, doc="荷受け人の事業者ID")
    carrier_cid = db.Column(db.String(50), nullable=True, doc="キャリアの事業者ID")
    trsp_instruction_id = db.Column(
        db.String(20), nullable=False, doc="trsp_instruction_id"
    )
    # 通常GIAIは最大３０桁
    tractor_giai = db.Column(
        db.String(34), nullable=True, doc="使用するトラクターのGIAI"
    )
    trailer_giai_list_str = db.Column(
        db.String(140),
        nullable=True,
        doc="使用するトレーラーのGIAIのリスト（カンマ区切りの文字列）",
    )
    req_from_time = db.Column(
        db.DateTime(timezone=True), nullable=True, doc="MH作業希望時間(From)"
    )
    req_to_time = db.Column(
        db.DateTime(timezone=True), nullable=True, doc="MH作業希望時間(To)"
    )
    actual_time = db.Column(
        db.DateTime(timezone=True), nullable=True, doc="MH作業実績時間"
    )
    status = db.Column(
        db.Integer, nullable=False, doc="状態(idle(0),planning(1),done(2),cancel(-1))"
    )
    is_bl_need = db.Column(
        db.Integer,
        nullable=False,
        server_default="0",
        doc="B/L 検証有無(着MHのみ1,それ以外は0)",
    )
    is_departure_mh = db.Column(
        db.Integer,
        nullable=False,
        server_default="1",
        doc="発MHなら1、着MHなら0",
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        doc="作成日時",
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        doc="更新日時",
    )

    @hybrid_property
    def mh_space_list(self) -> list[str]:
        if self.mh_space_list_str is None or self.mh_space_list_str == "":
            return []
        return self.mh_space_list_str.split(",")

    @hybrid_property
    def trailer_giai_list(self) -> list[str]:
        if self.trailer_giai_list_str is None or self.trailer_giai_list_str == "":
            return []
        return self.trailer_giai_list_str.split(",")


class DevanningPlanModelSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        ordered = True
        model = DevanningPlanModel
        load_instance = True
        exclude = ("id", "mh_space_list_str", "trailer_giai_list_str")

    id = ma.auto_field(
        metadata={"description": DevanningPlanModel.__table__.c.id.doc, "max_length": 5}
    )
    mh = ma.auto_field(
        metadata={
            "description": DevanningPlanModel.__table__.c.mh.doc,
            "max_length": 16,
            "example": "9930000010017",
        },
        validate=[validate.Length(max=16)],
    )
    mh_space_list = fields.List(
        fields.Str(),
        allow_none=False,
        metadata={
            "description": "MHの駐車枠のリスト",
            "example": ["1", "2"],
        },
    )
    shipper_cid = ma.auto_field(
        metadata={
            "description": DevanningPlanModel.__table__.c.shipper_cid.doc,
            "max_length": 50,
            "example": "990000001",
        },
        validate=[validate.Length(max=50)],
    )
    recipient_cid = ma.auto_field(
        metadata={
            "description": DevanningPlanModel.__table__.c.recipient_cid.doc,
            "max_length": 50,
            "example": "991000001",
        },
        validate=[validate.Length(max=50)],
    )
    carrier_cid = ma.auto_field(
        metadata={
            "description": DevanningPlanModel.__table__.c.carrier_cid.doc,
            "max_length": 50,
            "example": "992000001",
        },
        validate=[validate.Length(max=50)],
    )
    trsp_instruction_id = ma.auto_field(
        metadata={
            "description": DevanningPlanModel.__table__.c.trsp_instruction_id.doc,
            "max_length": 20,
            "example": "20241024",
        },
        validate=[validate.Length(max=20)],
    )
    tractor_giai = ma.auto_field(
        metadata={
            "description": DevanningPlanModel.__table__.c.tractor_giai.doc,
            "max_length": 34,
            "example": "8004990000001000000000000000000001",
        },
        validate=[validate.Length(max=34)],
    )
    trailer_giai_list = fields.List(
        fields.Str(),
        allow_none=True,
        metadata={
            "description": "使用するトレーラーのGIAIのリスト",
            "example": [
                "8004991000001000000000000000000001",
                "8004991000001000000000000000000002",
            ],
        },
    )
    req_from_time = ma.auto_field(
        metadata={
            "description": DevanningPlanModel.__table__.c.req_from_time.doc,
            "example": "2025/01/10 12:00",
        },
    )
    req_to_time = ma.auto_field(
        metadata={
            "description": DevanningPlanModel.__table__.c.req_to_time.doc,
            "example": "2025/01/10 12:10",
        },
    )
    actual_time = ma.auto_field(
        metadata={
            "description": DevanningPlanModel.__table__.c.actual_time.doc,
            "example": "2025/01/10 12:05",
        },
    )
    status = ma.auto_field(
        metadata={
            "description": DevanningPlanModel.__table__.c.status.doc,
            "example": 1,
        },
    )
    is_bl_need = ma.auto_field(
        metadata={
            "description": DevanningPlanModel.__table__.c.is_bl_need.doc,
            "example": 0,
        },
    )
    is_departure_mh = ma.auto_field(
        metadata={
            "description": DevanningPlanModel.__table__.c.is_departure_mh.doc,
            "example": 1,
        },
    )
    created_at = ma.auto_field(
        metadata={
            "description": DevanningPlanModel.__table__.c.created_at.doc,
            "example": "2025-01-01 15:00:00",
        },
    )
    updated_at = ma.auto_field(
        metadata={
            "description": DevanningPlanModel.__table__.c.updated_at.doc,
            "example": "2025-01-01 17:00:00",
        },
    )

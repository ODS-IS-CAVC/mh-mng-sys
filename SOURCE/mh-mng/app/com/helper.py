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

from flask_restx import fields
from datetime import time, datetime
from marshmallow import fields as ma_fields
import sys
import os
import importlib

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from database import db


def resolve_schema_from_string(schema_string):
    module_name, schema_name = schema_string.rsplit(".", 1)
    module = importlib.import_module(module_name)
    schemaInstance = getattr(module, schema_name)()
    return schemaInstance


class TimeField(fields.Raw):
    __schema_type__ = ["string"]

    def format(self, value):
        if isinstance(value, time):
            return str(value.strftime("%H:%M:%S"))
        elif isinstance(value, str):
            try:
                parsed_time = datetime.strptime(value, "%H:%M:%S")
                return parsed_time
            except ValueError:
                raise ValueError('Invalid time format, should be "%H:%M:%S"')
        raise ValueError("Invalid time format")

    def parse(self, value):
        if isinstance(value, str):
            try:
                parsed_time = datetime.strptime(value, "%H:%M:%S").time()
                return parsed_time
            except ValueError:
                raise ValueError('Invalid time format, should be "%H:%M:%S"')
        raise ValueError("Invalid time format")


def create_restx_model(model_name, api, model, exclude_fields=None):
    """It will convert a sqlalchemy model to a flask-restx model"""
    model_fields = {}
    if exclude_fields is None:
        exclude_fields = []
    for column in model.__table__.columns:
        description = column.doc or ""
        if column.name not in exclude_fields:
            if isinstance(column.type, db.Integer):
                model_fields[column.name] = fields.Integer(description=description)
            elif isinstance(column.type, db.String):
                model_fields[column.name] = fields.String(description=description)
            elif isinstance(column.type, db.DateTime):
                model_fields[column.name] = fields.DateTime(description=description)
    return api.model(model_name, model_fields)


# below method create model using the marshmallow schema
def create_restx_model_usingSchema(model_name, api, schema, exclude_fields=None):
    """It will convert a marshmallow schema to a flask-restx model"""
    model_fields = {}
    if exclude_fields is None:
        exclude_fields = []
    schema = schema() if isinstance(schema, type) else schema
    for field_name, field_obj in schema.fields.items():
        description = field_obj.metadata.get("description", "")
        if field_name not in exclude_fields:
            if isinstance(field_obj, ma_fields.Integer):
                max_length = field_obj.metadata.get("max_length")
                example = field_obj.metadata.get("example", 1)
                model_fields[field_name] = fields.Integer(
                    description=description, example=example, max_length=max_length
                )
            if isinstance(field_obj, ma_fields.Decimal):
                precision = field_obj.metadata.get("precision")
                scale = field_obj.metadata.get("scale")
                default_example = (
                    f"{'9' * (precision - scale)}.{('9' * scale)}"
                    if precision and scale
                    else None
                )
                example = field_obj.metadata.get("example", default_example)
                model_fields[field_name] = fields.String(
                    description=f"{description}\n Decimal field with precision {precision} and {scale}",
                    example=example,
                )
            elif isinstance(field_obj, ma_fields.String):
                max_length = field_obj.metadata.get("max_length")
                example = field_obj.metadata.get("example", "string")
                model_fields[field_name] = fields.String(
                    description=description, example=example, max_length=max_length
                )
            elif isinstance(field_obj, ma_fields.Date):
                example = field_obj.metadata.get("example", "2024-11-07")
                model_fields[field_name] = fields.Date(
                    description=description, example=example
                )
            elif isinstance(field_obj, ma_fields.Time):
                example = field_obj.metadata.get("example", "08:10:15")
                model_fields[field_name] = TimeField(
                    format="%H:%M:%S", description=description, example=""
                )
            elif isinstance(field_obj, ma_fields.DateTime):
                example = field_obj.metadata.get(
                    "example", "2024-11-07T23:41:50.409+09:00"
                )
                model_fields[field_name] = fields.DateTime(
                    description=description, example=example
                )
            elif isinstance(field_obj, ma_fields.Nested):
                nested_schema = field_obj.nested
                if isinstance(nested_schema, str):
                    nested_schema = resolve_schema_from_string(nested_schema)
                nested_name = f"{model_name}_{field_name}"
                nested_model = create_restx_model_usingSchema(
                    nested_name, api, nested_schema
                )
                model_fields[field_name] = fields.Nested(nested_model)
            elif isinstance(field_obj, ma_fields.List):
                list_name = f"{field_name}_list"
                if isinstance(field_obj.inner, ma_fields.Nested):
                    inner_schema = (
                        field_obj.inner.schema()
                        if isinstance(field_obj.inner.schema, type)
                        else field_obj.inner.schema
                    )
                    model_fields[field_name] = fields.List(
                        fields.Nested(
                            create_restx_model_usingSchema(list_name, api, inner_schema)
                        )
                    )
                elif isinstance(field_obj.inner, ma_fields.String):
                    model_fields[field_name] = fields.List(
                        fields.String(description=description, example=example)
                    )
                else:
                    model_fields[field_name] = fields.List(
                        create_restx_model_usingSchema(list_name, api, field_obj.inner)
                    )
    return api.model(model_name, model_fields)


def create_response_model(
    model_name, api, data_field_name, data_restx_model, list_type=False
):
    model_fields = {}
    if list_type is True:
        model_fields[data_field_name] = fields.List(fields.Nested(data_restx_model))
    else:
        model_fields[data_field_name] = fields.Nested(data_restx_model)
    model_fields["result"] = fields.Boolean(example=True, description="API結果")
    model_fields["error_msg"] = fields.String(
        example="", description="エラーメッセージ"
    )

    return api.model(model_name, model_fields)

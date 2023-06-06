from marshmallow import Schema, EXCLUDE, fields, RAISE, validate, post_dump
from enums.qr_code import QrCodeAction
from lib import ObjectIdField, Chains, BadRequest

import pydash as py_

from lib.enum import SUPPORTED_CHAIN_IDS


class QrCodeRequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    contract_address = fields.String(allow_none=True)
    index_type = fields.Integer(allow_none=True)
    nft_id = ObjectIdField(allow_none=True)
    amount = fields.Integer(allow_none=True)
    act = fields.String(
        validate=validate.OneOf([
            QrCodeAction.MINT,
            QrCodeAction.BUY
            
        ]),
        required=True
    )

    @post_dump
    def post_dump_qr(self, data, **kwargs):
        if data['act'] == QrCodeAction.MINT:
            if not py_.get(data, 'contract_address', None) or not py_.get(data, 'index_type', None):
                raise BadRequest(msg="Invalid data", errors=[
                    {
                        "contract_address": [
                            "Missing data for required field."
                        ]
                    },
                    {
                        "index_type": [
                            "Missing data for required field."
                        ]
                    },
                ])
            data['contract_address'] = data['contract_address'].lower()

        if data['act'] == QrCodeAction.BUY:
            if not py_.get(data, 'nft_id', None):
                raise BadRequest(msg="Invalid data", errors=[
                    {
                        "nft_id": [

                            "Missing data for required field."
                        ]
                    }
                ])


        return data

class QrCodeResponseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    qr_image_url = fields.String()
    qr_url = fields.String()

class PosQrCodeRequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    order_id = fields.String(required=True)
    amount = fields.Float(required=True, validate=validate.Range(min=1))
    currency = fields.String(required=True)
    rate_usd = fields.Float(required=True)
    fee_unit = fields.String(required=True)
    fee_value = fields.Float(required=True) 
    chain_id  = fields.Integer(required=True, validate=validate.OneOf(SUPPORTED_CHAIN_IDS))
    asset = fields.String(required=True)
    merchant_id = fields.String(required=True)
    serial_number = fields.String(required=True)
    act = fields.String(
        validate=validate.OneOf([
            QrCodeAction.DEPOSIT
        ]),
        required=True
    )

class PosQrResponseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    qr_url = fields.String()

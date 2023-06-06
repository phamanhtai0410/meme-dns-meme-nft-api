from marshmallow import Schema, EXCLUDE, fields
from lib import IsObjectId


class MintNftsRequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    nft_contract = fields.String(required=True)
    nft_type = fields.Integer(required=True)
    amount = fields.Integer(required=True)
    discount = fields.Float(required=False)
    is_whitelist_mint = fields.Bool(required=False)


class MintNftsStatusRequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.String(required=True, validate=IsObjectId())

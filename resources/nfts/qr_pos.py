# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from flask_restful import Resource
from pydash import get
from flask import request

from connect import security
from schemas import NFTsRequestSchema, NFTsResponseSchema
from schemas.nft.qr_code import PosQrCodeRequestSchema, QrCodeResponseSchema, PosQrResponseSchema
from services import NFTsServices
from services.nft.qr_metamask import QrService


class QrPosResource(Resource):

    @security.http(
        form_data=PosQrCodeRequestSchema(),
        response=PosQrResponseSchema()
    )
    def post(self, form_data):
        _response = QrService.generate_pos_qr(form_data=form_data)

        return _response

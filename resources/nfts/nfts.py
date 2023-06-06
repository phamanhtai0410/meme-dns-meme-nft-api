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
from services import NFTsServices


class NFTsResource(Resource):

    @security.http(
        params=NFTsRequestSchema(),
        response=NFTsResponseSchema()
    )
    def get(self, params):
        _contracts = request.args.getlist('contract[]', str)

        _response = NFTsServices.get_marketplace_by_contracts(params={
            **params,
            'contracts': _contracts
        })

        return _response

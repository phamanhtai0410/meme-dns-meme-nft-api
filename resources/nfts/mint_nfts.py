# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from flask_restful import Resource
from pydash import get

from connect import security
from schemas import MintNftsRequestSchema, MintNftsStatusRequestSchema
from services.nft.nft import NFTsServices


class MintNftsResource(Resource):

    @security.http(
        form_data=MintNftsRequestSchema(),
        login_required=True
    )
    def post(self, form_data, login_info):
        _response = NFTsServices.mint_nfts(user_id=get(login_info, 'user._id'), form_data=form_data)
        return _response

    @security.http(
        params=MintNftsStatusRequestSchema(),
        login_required=True
    )
    def get(self, params, login_info):
        _response = NFTsServices.mint_nfts_status(params=params)
        return _response

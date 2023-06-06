# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
__models__ = ['OrderModel', 'SignatureLogModel']

from config import Config
from connect import connect_db, redis_cluster
from lib import DaoModel
from models.order import OrderDao
from models.signature import SignatureDao
from models.nft import NftDao
from models.pos_transaction import PosTransactionsDao

NFTsModel = NftDao(col=connect_db.db.nft, redis=redis_cluster)
NFTContractsModel = DaoModel(col=connect_db.db.nft_contracts, redis=redis_cluster)
UsersContractsModel = DaoModel(col=connect_db.db.users_contracts, redis=redis_cluster)
UsersTemplatesModel = DaoModel(col=connect_db.db.users_templates, redis=redis_cluster)
CryptoCurrenciesModel = DaoModel(col=connect_db.db.crypto_currencies, redis=redis_cluster)

OrderModel = OrderDao(col=connect_db.db.orders, redis=redis_cluster, project=Config.PROJECT, broker=Config.BROKER_URL)
DevMintOrdersModel = OrderDao(col=connect_db.db.dev_mint_orders, redis=redis_cluster, project=Config.PROJECT, broker=Config.BROKER_URL)
SignatureLogModel = SignatureDao(col=connect_db.db.signature_log, redis=redis_cluster, project=Config.PROJECT, broker=Config.BROKER_URL)

QrCodeModel = DaoModel(col=connect_db.db.qr_code, redis=redis_cluster)

UsersModel = DaoModel(col=connect_db.db.users)

PosContractsModel = DaoModel(col=connect_db.db.pos_contracts, redis=redis_cluster)
PosTransactionsModel = PosTransactionsDao(col=connect_db.db.pos_transactions, redis=redis_cluster, project=Config.PROJECT, broker=Config.BROKER_URL)

WhitelistModel = SignatureDao(col=connect_db.db.whitelist, redis=redis_cluster, project=Config.PROJECT, broker=Config.BROKER_URL)

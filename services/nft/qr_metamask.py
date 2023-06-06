import traceback
import web3
import pydash as py_
import bson
import sentry_sdk
from config import Config
from enums.qr_code import QrCodeAction
from exceptions.nft_contract import NftContractNotFoundEx, NftIndexTypeNotFoundEx
from exceptions.nfts import NftNotFoundEx
from exceptions.pos_contracts import CurrencyPosContractNotFoundEx, PosContractNotFoundEx
from exceptions.qr_code import QRCodeNotFoundEx
from lib.enums.pos_contract import PosContractType, PosTransactionStatus

from models import NFTContractsModel, NFTsModel, PosContractsModel, PosTransactionsModel, QrCodeModel
from worker import worker
import bson.json_util


class QrService:

    @staticmethod
    def generate_innovaz_qr(form_data):
        _contract_address = py_.get(form_data, 'contract_address')
        _qr_act = py_.get(form_data, 'act')
        _index_type = py_.get(form_data, 'index_type')

        if _qr_act == QrCodeAction.BUY:
            _nft_id = py_.get(form_data, 'nft_id')
            _nft = NFTsModel.find_one({
                '_id': _nft_id
            })
            if not _nft:
                raise NftNotFoundEx

            _contract_address = py_.get(_nft, 'contract')
            _index_type = py_.get(_nft, 'type')


        _nft_contract = NFTContractsModel.find_one({
            'contract': _contract_address
        })

        if not _nft_contract:
            raise NftContractNotFoundEx

        _filter = {}
        _properties = {}
        if  _qr_act == QrCodeAction.MINT:
            _filter = {
                'properties.act': QrCodeAction.MINT,
                'properties.chain_id': py_.get(_nft_contract, 'chain_id'),
                'properties.contract_address': py_.get(_nft_contract, 'dapp_creator_address'),
                'properties.nft_address': py_.get(_nft_contract, 'contract'),
                'properties.nft_type': py_.get(form_data, 'index_type'),
                'properties.amount': py_.get(form_data, 'amount'),
                'properties.price': py_.get(_nft_contract, f'nft_list.{_index_type - 1}.price'),
                'properties.currency_address': py_.get(_nft_contract, 'currency_address')
            }

            _properties = {
                'act': QrCodeAction.MINT,
                'chain_id': py_.get(_nft_contract, 'chain_id'),
                'contract_address': py_.get(_nft_contract, 'dapp_creator_address'),
                'nft_address': py_.get(_nft_contract, 'contract'),
                'nft_type': py_.get(form_data, 'index_type'),
                'amount': py_.get(form_data, 'amount'),
                'price': py_.get(_nft_contract, f'nft_list.{_index_type - 1}.price'),
                'currency_address': py_.get(_nft_contract, 'currency_address')
            }

        if _qr_act == QrCodeAction.BUY:
            _filter = {
                'properties.act': QrCodeAction.BUY,
                'properties.nft_id': bson.objectid.ObjectId(py_.get(form_data, 'nft_id'))
            }
            _properties = {
                'act': QrCodeAction.BUY,
                'nft_id': py_.get(form_data, 'nft_id')
            }

        _qr = QrCodeModel.find_one(_filter)
        print(_qr)
        if _qr:
            return _qr

        if not py_.get(_nft_contract, f'nft_list.{_index_type - 1}'):
            raise NftIndexTypeNotFoundEx

        _image_url = py_.get(_nft_contract, f'nft_list.{_index_type - 1}.image_url')

        worker.send_task('worker.task_generate_metamask_qr_code', (_image_url, bson.json_util.dumps(_properties)))

        raise QRCodeNotFoundEx

    @staticmethod
    def generate_pos_qr(form_data):
        '''
        {
            "order_id": "ggdeheh64738264876827dgehegdh7",
            "amount": 23000000,
            "currency": "VND",
            "rate_usd": 23620.00,
            "fee_unit": "fixed",
            "fee_value": 1, // usd
            "chain_id": 94,
            "asset": "USDT",
            "merchant_id": "123",
            "serial_number":"000000020230102"
        } 
        '''
        def convert_rate_amount():
            _pos_amount = py_.get(form_data, 'amount')
            _rate_usd = py_.get(form_data, 'rate_usd')
            _fee_value = py_.get(form_data, 'fee_value')

            _amount = round(_pos_amount / _rate_usd + _fee_value, 6)

            return _amount
        
        def generate_qr_url(properties):
            _url = f'{Config.INNOVAZ_PAYMENT_URL}/qr-scan?'
            for _prop in properties:
                _url += f'&{_prop}={properties[_prop]}'

            return _url

        _chain_id = py_.get(form_data, 'chain_id')
        _qr_act = py_.get(form_data, 'act')
        _order_id = py_.get(form_data, 'order_id')
        _asset = py_.get(form_data, 'asset')

        _pos_contract = PosContractsModel.find_one({
            'chain_id': _chain_id,
            'type': PosContractType.CONTRACT
        })

        if not _pos_contract:
            raise PosContractNotFoundEx

        _currency_pos_contract = PosContractsModel.find_one({
            'chain_id': _chain_id,
            'type': PosContractType.CURRENCY,
            'asset': _asset
        })
        if not _currency_pos_contract:
            raise CurrencyPosContractNotFoundEx

        _currency_address = py_.get(_currency_pos_contract, 'contract_address')
        _contract_address = py_.get(_pos_contract, 'contract_address')

        _amount = convert_rate_amount()

        # _filter = {}
        _properties = {}
        if _qr_act == QrCodeAction.DEPOSIT:
            # _filter = {
            #     'properties.order_id': _order_id
            # }

            _properties = {
                'order_id': _order_id,
                'contract_address': _contract_address,
                'currency_address': _currency_address,
                'transaction_amount': _amount,
                'act': QrCodeAction.DEPOSIT,
                'chain_id': _chain_id
            }

        _qr_url = generate_qr_url(properties=_properties)

        # _qr = QrCodeModel.find_one(filter=_filter)

        # if _qr:
        #     return _qr

        PosTransactionsModel.update_one({
            'order_id': _order_id
        },{
            **form_data,
            'status': PosTransactionStatus.PENDING,
            'transaction_amount': _amount,
            'contract_address': _contract_address,
            'currency_address': _currency_address,
            'act': QrCodeAction.DEPOSIT,
            'chain_id': _chain_id,
            'updated_by': 'inz-nft-api:services:QrService:generate_pos_qr'
        }, upsert=True)

        # worker.send_task('worker.task_generate_pos_qr_code', (bson.json_util.dumps(_properties), ))

        return {
            'qr_url': _qr_url
        }
        
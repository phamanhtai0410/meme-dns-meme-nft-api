import uuid
import pydash as py_
from enums.contract import ContractStandard
from enums.signature import SignatureType
from exceptions.nft_contract import NftContractNotFoundEx, NftContractUserNotInWhitelistEx
from exceptions.nfts import CurrencyTokenNotExceptEx, NftIsNotOnMarketEx, NftIsOnMarketEx, UserNotOwnNftEx
from exceptions.trade_nft import NftTradeOwnerAddressCanNotEqualToAddress
from exceptions.user import UserNotHaveAddressEx

from helper.signature import SignatureHelper
from models import CryptoCurrenciesModel, NFTContractsModel, NFTsModel, SignatureLogModel, UsersModel, WhitelistModel
from services.nft.nft import NFTsServices


class SMCSignatureService:

    @staticmethod
    def create_signature(form_data):
        # NOTE: does not have rule about discount and whitelist yet
        _discount = int(0)
        _is_whitelist = False
        _user_address = py_.get(form_data, 'user_address').lower()
        _contract_address = py_.get(form_data, 'contract_address').lower()
        _nft_address = py_.get(form_data, 'nft_address').lower()

        _sign_data = {
            **form_data,
            'user_address': _user_address,
            'contract_address': _contract_address,
            'nft_address': _nft_address,
            'discount': _discount,
            'is_whitelist': _is_whitelist
        }

        _nft_contract = NFTContractsModel.find_one({
            'contract': _nft_address
        })

        if not _nft_contract:
            raise NftContractNotFoundEx

        _is_whitelist_mint = py_.get(_nft_contract, 'is_whitelist_mint')

        if _is_whitelist_mint:
            _check_whitelist = WhitelistModel.find_one({
                'user_address': _user_address,
                'contract_address': _nft_address
            })

            if not _check_whitelist:
                raise NftContractUserNotInWhitelistEx

            _is_whitelist = True

        
        _signature, _deadline = SignatureHelper.generate_signature(data=_sign_data)

        _log_id = str(uuid.uuid4())

        SignatureLogModel.insert_one({
            **_sign_data,
            'log_id': _log_id,
            'signature': _signature,
            'deadline': _deadline,
            'type': SignatureType.MINT,
            'currency': py_.get(_nft_contract, 'currency'),
            'dapp_creator_address': py_.get(_nft_contract, 'dapp_creator_address'),
            'currency_address': py_.get(_nft_contract, 'currency_address'),
            'created_by': 'inz-nft-api:SMCSignatureService:SM:create_signature'
        }, worker=True)

        return {
            'data': {
                **_sign_data,
                'callback': _log_id
            },
            'signature': _signature,
            'deadline': _deadline
        }

    @staticmethod
    def create_buy_nft_signature(form_data):

        _chain_id = py_.get(form_data, 'chain_id')
        _nft_id = py_.get(form_data, 'nft_id')
        _to_address = py_.get(form_data, 'to_address')

        _nft = NFTsModel.find_one({
            '_id': _nft_id
        })
        if not _nft or not NFTsServices.is_nft_on_market(item=_nft):
            raise NftIsNotOnMarketEx

        _owner_id = py_.get(_nft, 'user')

        _user = UsersModel.find_one({
            '_id': _owner_id
        })
        if not _user:
            raise UserNotOwnNftEx

        _owner_address = py_.get(_user, 'public_address', None)

        if not _owner_address:
            raise UserNotHaveAddressEx

        if _owner_address.lower() == _to_address.lower():
            raise NftTradeOwnerAddressCanNotEqualToAddress

        _nft_contract = NFTContractsModel.find_one({
            'contract': py_.get(_nft, 'contract')
        })
        if not _nft_contract or py_.get(_nft_contract, 'chain_id') != _chain_id:
            raise NftContractNotFoundEx

        _currency_address = py_.get(_nft, 'currency_address')
        _currency = CryptoCurrenciesModel.find_one({
            'contract_address': _currency_address
        })

        if not _currency:
            raise CurrencyTokenNotExceptEx

        _contract_standard = 1 if py_.get(_nft_contract, 'standard') == ContractStandard.ERC1155 else 0

        _sign_data = {
            'chain_id': _chain_id,
            'order_id': py_.get(_nft, 'order_id'),
            'to_address': _to_address,
            'nft_address': py_.get(_nft, 'contract'),
            'currency_address': _currency_address,
            'token_id': py_.get(_nft, 'token_id'),
            'price': py_.get(_nft, 'price'),
            'owner_address': _owner_address,
            'currency_decimal': py_.get(_currency, 'decimal'),
            'standard': _contract_standard
        }

        _signature_data =  SignatureHelper.generate_buy_nft_signature(data=_sign_data)

        _log_id = str(uuid.uuid4())

        SignatureLogModel.insert_one({
            **_sign_data,
            'log_id': _log_id,
            'signature': py_.get(_signature_data, 'signature'),
            'deadline': py_.get(_signature_data, 'deadline'),
            'type': SignatureType.BUY,
            'created_by': 'inz-nft-api:SMCSignatureService:SM:create_buy_nft_signature'
        }, worker=True)

        return _signature_data

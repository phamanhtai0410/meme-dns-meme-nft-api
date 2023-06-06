class PosContractNotFoundEx(Exception):
    def __init__(self, msg='pos contract not found', *args: object, **kwargs) -> None:
        super().__init__(*args)
        self.status_code = 400
        self.msg = msg
        self.errors = kwargs.get('errors', [])
        self.error_code = 'E_POS_CONTRACT_NOT_FOUND'

    pass

class CurrencyPosContractNotFoundEx(Exception):
    def __init__(self, msg='currency pos contract not found', *args: object, **kwargs) -> None:
        super().__init__(*args)
        self.status_code = 400
        self.msg = msg
        self.errors = kwargs.get('errors', [])
        self.error_code = 'E_CURRENCY_POS_CONTRACT_NOT_FOUND'

    pass

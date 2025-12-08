class AssetBaseException(Exception):
    """기본 커스텀 예외"""
    def __init__(self, message="An error occurred", code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class StockDataFetchError(AssetBaseException):
    """주식 데이터 수집 중 발생하는 예외"""
    pass


class CryptoDataFetchError(AssetBaseException):
    """암호화폐 데이터 수집 중 발생하는 예외"""
    pass


class KakaoAPIError(AssetBaseException):
    """카카오 API 호출 중 발생하는 예외"""
    pass


class ReportGenerationError(AssetBaseException):
    """리포트 생성 중 발생하는 예외"""
    pass


class ValidationError(AssetBaseException):
    """비즈니스 로직 검증 중 발생하는 예외"""
    pass

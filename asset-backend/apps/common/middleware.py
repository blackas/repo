import logging
import time
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    모든 HTTP 요청/응답을 로깅하는 미들웨어
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        # 요청 로깅
        logger.info(
            f"Request: {request.method} {request.path} "
            f"from {request.META.get('REMOTE_ADDR')}"
        )

        response = self.get_response(request)

        # 응답 시간 계산
        duration = time.time() - start_time

        # 응답 로깅
        logger.info(
            f"Response: {response.status_code} "
            f"for {request.method} {request.path} "
            f"({duration:.2f}s)"
        )

        return response


class ExceptionHandlingMiddleware:
    """
    전역 예외 처리 미들웨어
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.error(
            f"Exception occurred: {exception.__class__.__name__}: {str(exception)}",
            exc_info=True,
            extra={
                "request_path": request.path,
                "request_method": request.method,
            }
        )

        if request.path.startswith("/api/"):
            return JsonResponse(
                {
                    "error": "Internal Server Error",
                    "message": str(exception) if logger.level == logging.DEBUG else "An error occurred"
                },
                status=500
            )

        return None

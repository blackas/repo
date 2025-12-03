import logging
import requests
from django.conf import settings
from apps.common.exceptions import KakaoAPIError
from apps.common.utils import retry_on_failure, log_execution_time, mask_sensitive_data

logger = logging.getLogger(__name__)


class KakaoAlimtalkClient:
    def __init__(self):
        self.host = settings.KAKAO_API_HOST.rstrip("/")
        self.api_key = settings.KAKAO_API_KEY
        self.sender_key = settings.KAKAO_SENDER_KEY

        # API 설정 검증
        if not self.host:
            logger.warning("KAKAO_API_HOST is not configured")
        if not self.api_key:
            logger.warning("KAKAO_API_KEY is not configured")
        if not self.sender_key:
            logger.warning("KAKAO_SENDER_KEY is not configured")

    @log_execution_time
    @retry_on_failure(max_retries=2, delay=1.0)
    def send_message(
        self,
        to_phone: str,
        template_code: str,
        message: str,
        button_url: str | None = None
    ) -> dict:
        """
        카카오 알림톡 메시지 전송

        Args:
            to_phone: 수신자 전화번호
            template_code: 템플릿 코드
            message: 메시지 내용
            button_url: 버튼 URL (선택사항)

        Returns:
            발송 결과 딕셔너리

        Raises:
            KakaoAPIError: API 호출 실패 시
        """
        masked_phone = mask_sensitive_data(to_phone, visible_chars=3)
        logger.info(f"Sending Kakao message to {masked_phone}, template: {template_code}")

        # API 설정 확인
        if not all([self.host, self.api_key, self.sender_key]):
            raise KakaoAPIError("Kakao API configuration is incomplete")

        try:
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {self.api_key}",
            }

            payload = {
                "senderKey": self.sender_key,
                "templateCode": template_code,
                "recipientList": [
                    {
                        "recipientNo": to_phone,
                        "message": message,
                        "btns": [],
                    }
                ],
            }

            if button_url:
                payload["recipientList"][0]["btns"].append(
                    {
                        "type": "WL",
                        "name": "상세보기",
                        "linkMobile": button_url,
                        "linkPc": button_url,
                    }
                )

            logger.debug(f"Sending request to {self.host}/v2/api/alimtalk/send")

            resp = requests.post(
                f"{self.host}/v2/api/alimtalk/send",
                json=payload,
                headers=headers,
                timeout=5,
            )

            result = {
                "status_code": resp.status_code,
                "body": resp.text,
                "payload": payload,
            }

            if resp.status_code == 200:
                logger.info(f"Successfully sent message to {masked_phone}")
            else:
                logger.warning(
                    f"Kakao API returned non-200 status: {resp.status_code}, "
                    f"response: {resp.text[:200]}"
                )

            return result

        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout sending message to {masked_phone}: {e}")
            raise KakaoAPIError(f"Kakao API timeout: {e}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error sending message to {masked_phone}: {e}")
            raise KakaoAPIError(f"Kakao API request failed: {e}")

        except Exception as e:
            logger.error(
                f"Unexpected error sending message to {masked_phone}: {e}",
                exc_info=True
            )
            raise KakaoAPIError(f"Unexpected error: {e}")

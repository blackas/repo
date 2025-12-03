"""
페이지네이션 스키마
"""
from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """
    페이지네이션 응답 스키마

    Attributes:
        total: 전체 아이템 수
        page: 현재 페이지 번호 (1부터 시작)
        page_size: 페이지당 아이템 수
        total_pages: 전체 페이지 수
        items: 현재 페이지의 아이템 리스트
    """
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[T]

    @classmethod
    def create(cls, items: List[T], total: int, page: int, page_size: int):
        """
        페이지네이션 응답 생성 헬퍼 메서드

        Args:
            items: 현재 페이지의 아이템 리스트
            total: 전체 아이템 수
            page: 현재 페이지 번호
            page_size: 페이지당 아이템 수

        Returns:
            PaginatedResponse 인스턴스
        """
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return cls(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            items=items
        )

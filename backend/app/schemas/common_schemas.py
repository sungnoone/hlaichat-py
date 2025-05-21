from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel
from pydantic.generics import GenericModel

# 定義泛型類型變數
T = TypeVar("T")

class ResponseBase(BaseModel):
    """
    基本回應模型
    """
    success: bool = True
    message: str = "操作成功"

class DataResponse(ResponseBase, Generic[T]):
    """
    帶資料的回應模型
    """
    data: Optional[T] = None

class PaginatedResponseBase(ResponseBase):
    """
    分頁回應基本模型
    """
    total: int
    page: int
    page_size: int
    total_pages: int

class PaginatedResponse(PaginatedResponseBase, Generic[T]):
    """
    分頁回應模型
    """
    items: List[T]

class ErrorResponse(ResponseBase):
    """
    錯誤回應模型
    """
    success: bool = False
    message: str = "操作失敗"
    error_code: Optional[str] = None
    details: Optional[Any] = None

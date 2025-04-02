from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class volunteerInfo(_message.Message):
    __slots__ = ("userId", "userAddress")
    USERID_FIELD_NUMBER: _ClassVar[int]
    USERADDRESS_FIELD_NUMBER: _ClassVar[int]
    userId: str
    userAddress: str
    def __init__(self, userId: _Optional[str] = ..., userAddress: _Optional[str] = ...) -> None: ...

class inputBody(_message.Message):
    __slots__ = ("productId", "productAddress", "productCCAddress", "volunteerList")
    PRODUCTID_FIELD_NUMBER: _ClassVar[int]
    PRODUCTADDRESS_FIELD_NUMBER: _ClassVar[int]
    PRODUCTCCADDRESS_FIELD_NUMBER: _ClassVar[int]
    VOLUNTEERLIST_FIELD_NUMBER: _ClassVar[int]
    productId: str
    productAddress: str
    productCCAddress: str
    volunteerList: _containers.RepeatedCompositeFieldContainer[volunteerInfo]
    def __init__(self, productId: _Optional[str] = ..., productAddress: _Optional[str] = ..., productCCAddress: _Optional[str] = ..., volunteerList: _Optional[_Iterable[_Union[volunteerInfo, _Mapping]]] = ...) -> None: ...

class responseBody(_message.Message):
    __slots__ = ("productId", "userList", "error")
    PRODUCTID_FIELD_NUMBER: _ClassVar[int]
    USERLIST_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    productId: str
    userList: _containers.RepeatedScalarFieldContainer[str]
    error: str
    def __init__(self, productId: _Optional[str] = ..., userList: _Optional[_Iterable[str]] = ..., error: _Optional[str] = ...) -> None: ...

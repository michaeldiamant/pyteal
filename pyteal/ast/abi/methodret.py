from typing import TYPE_CHECKING

from .type import Type
from ..seq import Seq
from ..naryexpr import Concat
from ..unaryexpr import Log
from ...errors import verifyTealVersion
from ...types import TealType
from ...config import RETURN_EVENT_SELECTOR
from ...ir import Op
from ..expr import Expr

if TYPE_CHECKING:
    from ...compiler import CompileOptions


class MethodReturn(Expr):
    def __init__(self, value: Type) -> None:
        super().__init__()
        self.value = value

    def __teal__(self, options: "CompileOptions"):
        verifyTealVersion(
            Op.log.min_version, options.version, "TEAL version too low to use log"
        )
        return Log(Concat(RETURN_EVENT_SELECTOR, self.value.encode())).__teal__(
            options=options
        )

    def __str__(self) -> str:
        return "(MethodReturn {})".format(self.value)

    def type_of(self) -> TealType:
        return TealType.none

    def has_return(self) -> bool:
        return False


MethodReturn.__module__ = "pyteal"

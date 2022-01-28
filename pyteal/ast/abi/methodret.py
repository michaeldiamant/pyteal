from typing import TYPE_CHECKING

from ...ast.naryexpr import Concat
from ...ast.unaryexpr import Log
from ...errors import TealCompileError, verifyTealVersion
from ...ir.ops import Op
from ...types import TealType, types_match
from ...config import RETURN_EVENT_SELECTOR
from ..expr import Expr

if TYPE_CHECKING:
    from ...compiler import CompileOptions


class MethodReturn(Expr):
    def __init__(self, value: Expr) -> None:
        super().__init__()
        self.value = value

    def __teal__(self, options: "CompileOptions"):
        if types_match(self.value.type_of(), TealType.bytes):
            verifyTealVersion(
                Op.log.min_version, options.version, "TEAL version too low to use log"
            )
            concatLogExpr = Log(Concat(RETURN_EVENT_SELECTOR, self.value))
            return concatLogExpr.__teal__(options=options)
        elif types_match(self.value.type_of(), TealType.none):
            return self.value.__teal__(options=options)
        else:
            raise TealCompileError(
                "method return cannot handle types other than TealType.none or TealType.bytes",
                self,
            )

    def __str__(self) -> str:
        return "(MethodReturn {})".format(self.value)

    def type_of(self) -> TealType:
        return TealType.none

    def has_return(self) -> bool:
        return False


MethodReturn.__module__ = "pyteal"

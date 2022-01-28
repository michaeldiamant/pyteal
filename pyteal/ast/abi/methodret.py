from typing import TYPE_CHECKING

from ..naryexpr import Concat
from ..unaryexpr import Log
from ..subroutine import SubroutineCall
from ...errors import TealCompileError, TealInputError, verifyTealVersion
from ...ir.ops import Op
from ...types import TealType
from ...config import RETURN_EVENT_SELECTOR
from ..expr import Expr

if TYPE_CHECKING:
    from ...compiler import CompileOptions


class MethodReturn(Expr):
    def __init__(self, value: Expr) -> None:
        super().__init__()
        if not isinstance(value, SubroutineCall):
            raise TealInputError(
                "method return can only be applied to handle method handler subroutine"
            )
        if not value.subroutine.getDeclaration().has_return():
            raise TealInputError(
                "method return do not accept method handler (subroutine) with no return"
            )
        self.value = value

    def __teal__(self, options: "CompileOptions"):
        if self.value.type_of() == TealType.bytes:
            verifyTealVersion(
                Op.log.min_version, options.version, "TEAL version too low to use log"
            )
            concatLogExpr = Log(Concat(RETURN_EVENT_SELECTOR, self.value))
            return concatLogExpr.__teal__(options=options)
        elif self.value.type_of() == TealType.none:
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

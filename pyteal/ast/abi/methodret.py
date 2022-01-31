from typing import TYPE_CHECKING

from pyteal.ast.return_ import Return
from pyteal.ast.seq import Seq

from ..naryexpr import Concat
from ..unaryexpr import Log
from ...errors import TealCompileError, TealInputError, verifyTealVersion
from ...ir.ops import Op
from ...types import TealType, types_match
from ...config import RETURN_EVENT_SELECTOR
from ..expr import Expr
from .type import Type

if TYPE_CHECKING:
    from ...compiler import CompileOptions


class MethodReturn(Expr):
    def __init__(self, value: Type = None) -> None:
        super().__init__()
        self.value = value

    def __teal__(self, options: "CompileOptions"):
        if options.currentSubroutine is None:
            raise TealInputError("method return must be used in subroutines")

        verifyTealVersion(
            Op.retsub.min_version,
            options.version,
            "TEAL verison too low to use subroutines",
        )

        returnType = options.currentSubroutine.returnType
        if returnType == TealType.none:
            if self.value is not None:
                raise TealCompileError(
                    "Cannot return an ABI value from a subroutine with return type TealType.none",
                    self,
                )
        else:
            if self.value is None:
                raise TealCompileError(
                    "Cannot return nothing from a subroutine is declared to have return type",
                    self,
                )
            if not types_match(TealType.bytes, returnType):
                raise TealCompileError(
                    "Incompatible return type from subroutine, should return bytes but subroutine specified {}".format(
                        returnType
                    ),
                    self,
                )

        if self.value is None:
            return Return().__teal__(options)
        else:
            return Seq(
                Log(Concat(RETURN_EVENT_SELECTOR, self.value.encode())), Return()
            ).__teal__(options)

    def __str__(self) -> str:
        return "(MethodReturn {})".format(self.value)

    def type_of(self) -> TealType:
        return TealType.none

    def has_return(self) -> bool:
        return False


MethodReturn.__module__ = "pyteal"

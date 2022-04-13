from dataclasses import dataclass
from typing import TypeVar, Generic

from pyteal import *
from pyteal.ast.abi import BaseType, Uint64TypeSpec

# The snippet explores a representation that does _not_ conform to the @Subroutine requirement to return `Expr`.
#
# Perceived point of friction:  Retaining a reference to an ABI type while accumulating the program AST via `Expr`.
# * Simply returning `Expr` loses the specificity provided by an ABI type.
# * Encoding the needed information requires marshalling return values with a flow that's out of the user's control (e.g. via decorator) and does _not_ match typical function invocation.
#
# Tradeoff:  The approach provides a hopefully more familiar programming model at the expense of enabling ABI return types from `@Subroutine`.
# * The snippet makes no attempt to provide an annotation for denoting _subroutines_.  If the approach is palatable, annotations can be added.
# * It's possible to imagine something like `@AbiSubroutine` for ABI-specific subroutines.  It might be the case that we want to differentiate between ARC-4 methods and internal methods with distinct annotations.

T = TypeVar("T", bound=BaseType)

# AbiSeq is a specialized Tuple2 for encoding `Expr` and an underlying ABI type.
# It's intended to be a return value for functions operating on a return ABI type.
#
# While AbiSeq can be replaced wtih Tuple2 today, it's possible to imagine enriching the representation.   For example, combinators and convenience methods for operating over multiple `AbiSeq`s might exist.
@dataclass
class AbiSeq(Generic[T]):
    expr: Expr
    value: T


def sum(to_sum: abi.DynamicArray[abi.Uint64]) -> AbiSeq[abi.Uint64]:
    i = ScratchVar(TealType.uint64)
    value_at_index = abi.Uint64()
    acc = abi.Uint64()
    return AbiSeq(
        For(i.store(Int(0)), i.load() < to_sum.length(), i.store(i.load() + Int(1))).Do(
            Seq(
                to_sum[i.load()].store_into(value_at_index),
                acc.set(acc.get() + value_at_index.get()),
            )
        ),
        acc,
    )


def multiply(to_multiply: abi.DynamicArray[abi.Uint64]) -> AbiSeq[abi.Uint64]:
    i = ScratchVar(TealType.uint64)
    value_at_index = abi.Uint64()
    acc = abi.Uint64()
    return AbiSeq(
        Seq(
            acc.set(1),
            For(
                i.store(Int(0)),
                i.load() < to_multiply.length(),
                i.store(i.load() + Int(1)),
            ).Do(
                Seq(
                    to_multiply[i.load()].store_into(value_at_index),
                    acc.set(acc.get() * value_at_index.get()),
                )
            ),
        ),
        acc,
    )


def sum_and_multiply(
    to_sum: abi.DynamicArray[abi.Uint64], to_multiply: abi.DynamicArray[abi.Uint64]
) -> AbiSeq[abi.Tuple2[abi.Uint64, abi.Uint64]]:
    z = abi.Tuple2(Uint64TypeSpec(), Uint64TypeSpec())
    a = sum(to_sum)
    b = multiply(to_multiply)

    return AbiSeq(Seq(a.expr, b.expr), z)


def log_abi_result(result: T) -> Expr:
    return Log(result.encode())


def unapply(a: AbiSeq[T]) -> (Expr, T):
    return a.expr, a.value


# Returns a Seq to be invoked via `compileTeal`.
def build_program() -> Expr:
    def parse_inputs() -> (
        Expr,
        abi.DynamicArray[abi.Uint64TypeSpec()],
        abi.DynamicArray[abi.Uint64TypeSpec()],
    ):
        x = abi.DynamicArray(abi.Uint64TypeSpec())
        y = abi.DynamicArray(abi.Uint64TypeSpec())
        return (
            Seq(
                x.decode(Txn.application_args[0]),
                y.decode(Txn.application_args[1]),
            ),
            x,
            y,
        )

    # Composing the main program requires considerable manual value stitching.
    # It's possible to imagine removing boilerplate with combinators built atop `AbiSeq`.
    (a, to_sum, to_multiply) = parse_inputs()
    (b, z) = unapply(sum_and_multiply(to_sum, to_multiply))
    c = log_abi_result(z)
    return Seq(a, b, c)

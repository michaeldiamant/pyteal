import pytest

from ... import *

options = CompileOptions(version=5)


"""
def test_method_return_subroutine_log():
    @Subroutine(TealType.bytes, "ork()byte[13]")
    def ork() -> Expr:
        return Return(Bytes("gork and mork"))

    logReturn = abi.MethodReturn(ork())


def test_method_return_subroutine_void():
    @Subroutine(TealType.none, "kiwibird(byte[8])void")
    def kiwibird(worm: Expr):
        return Return()

    eatWorm = abi.MethodReturn(kiwibird(Bytes("iamaworm")))


def test_method_return_subroutine_no_ret():
    pass


def test_method_return_subroutine_wrong_type():
    @Subroutine(TealType.uint64, "badNumber(uint64)uint64")
    def badNumber(a: Expr) -> Expr:
        return Return(Int(0xDEADBEEF) + a)

    with pytest.raises(TealCompileError):
        abi.MethodReturn(badNumber(Int(114514))).__teal__(options=options)

    @Subroutine(TealType.anytype, "fakeUint64()byte[8]")
    def fakeUint64() -> Expr:
        return Return(Bytes("fakeuint"))

    with pytest.raises(TealCompileError):
        abi.MethodReturn(fakeUint64()).__teal__(options=options)
"""

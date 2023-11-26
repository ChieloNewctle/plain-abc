import sys
from abc import ABC, abstractmethod
from enum import Enum
from typing import Literal

import pytest
from plain_abc import MissingImplError, NameConflictError, PlainABC, WrongImplError


class _HiddenMetaclass(type):
    pass


class ARecord(metaclass=_HiddenMetaclass):
    def __init__(self, a=0):
        self.a = a
        super().__init__()


def test_metaclass_conflict():
    with pytest.raises(TypeError):

        class IFoo(ABC):
            @abstractmethod
            def foo(self, a):
                ...

        class _(ARecord, IFoo):  # pyright: ignore
            ...


def test_normal():
    class IFoo(PlainABC):
        @abstractmethod
        def foo(self, a):
            ...

        @classmethod
        @abstractmethod
        def foo_classmethod(cls):
            ...

        @staticmethod
        @abstractmethod
        def foo_staticmethod():
            ...

        @property
        @abstractmethod
        def bar(cls):
            ...

        def hmm(self):
            return self

    class INewFoo(IFoo, PlainABC):
        @abstractmethod
        def new_foo(self):
            ...

        def hmm(self):
            return 5

    class Foo(ARecord, INewFoo):
        def foo(self, a):
            return self.a + a

        def new_foo(self):
            return self.a + 1

        @classmethod
        def foo_classmethod(cls):
            return 9

        @staticmethod
        def foo_staticmethod():
            return 8

        @property
        def bar(cls):
            return 7

    assert Foo(3).foo(4) == 3 + 4
    assert Foo(a=5).new_foo() == 5 + 1
    assert Foo().hmm() == 5
    assert Foo.foo_classmethod() == 9
    assert Foo.foo_staticmethod() == 8
    assert Foo().bar == 7


def test_multiple():
    class IFoo(PlainABC):
        @abstractmethod
        def foo(self, a):
            ...

    class INewFoo(PlainABC):
        @abstractmethod
        def new_foo(self):
            ...

    class Foo(ARecord, IFoo, INewFoo):
        def foo(self, a):
            return self.a + a

        def new_foo(self):
            return self.a + 1

    assert Foo(3).foo(4) == 3 + 4
    assert Foo(a=5).new_foo() == 5 + 1


def test_missing_impl():
    class IFoo(PlainABC):
        @abstractmethod
        def foo(self, a):
            ...

    with pytest.raises(MissingImplError):

        class _(ARecord, IFoo):
            ...


def test_missing_impl_classmethod():
    class IFoo(PlainABC):
        @classmethod
        @abstractmethod
        def foo(cls, a):
            ...

    with pytest.raises(MissingImplError):

        class _(ARecord, IFoo):
            ...


def test_missing_impl_staticmethod():
    class IFoo(PlainABC):
        @staticmethod
        @abstractmethod
        def foo(a):
            ...

    with pytest.raises(MissingImplError):

        class _(ARecord, IFoo):
            ...


def test_missing_impl_property():
    class IFoo(PlainABC):
        @property
        @abstractmethod
        def foo(self):
            ...

    with pytest.raises(MissingImplError):

        class _(ARecord, IFoo):
            ...


def test_wrong_impl():
    class IFoo(PlainABC):
        @abstractmethod
        def foo(self, a):
            ...

    with pytest.raises(WrongImplError):

        class _(ARecord, IFoo):
            def foo(self, a, b):
                return a + b


def test_conflict():
    class IFooA(PlainABC):
        @abstractmethod
        def foo(self, a):
            ...

    class IFooB(PlainABC):
        @abstractmethod
        def foo(self, a):
            ...

    with pytest.raises(NameConflictError):

        class _(ARecord, IFooA, IFooB):
            ...


def test_use_attribute_as_property():
    class IFoo(PlainABC):
        @property
        @abstractmethod
        def foo(self):
            ...

    class Foo(ARecord, IFoo):
        foo = "foo"  # pyright: ignore

    assert Foo.foo == "foo"


def test_string_enum():
    class IWordSizeEnum(PlainABC):
        @property
        @abstractmethod
        def x32(self) -> Literal["x32"]:
            ...

        @property
        @abstractmethod
        def x64(self) -> Literal["x64"]:
            ...

    if sys.version_info < (3, 11):

        class WordSizeEnum(IWordSizeEnum, Enum):
            __abc_concrete_members__ = ("x32", "x64")
            x32 = "x32"  # pyright: ignore
            x64 = "x64"  # pyright: ignore

    else:

        class WordSizeEnum(IWordSizeEnum, Enum):
            x32 = "x32"  # pyright: ignore
            x64 = "x64"  # pyright: ignore

    assert WordSizeEnum.x32.value == "x32"  # pyright: ignore
    assert WordSizeEnum.x64.value == "x64"  # pyright: ignore

from abc import ABC, abstractmethod

import pytest

from plain_abc import (MissingImplError, NameConflictError, PlainABC,
                       WrongImplError)


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

        class _(ARecord, IFoo):   # pyright: ignore
            ...


def test_plain_abc_normal():
    class IFoo(PlainABC):
        @classmethod
        @abstractmethod
        def create(cls, *args, **kwargs):
            ...

        @abstractmethod
        def foo(self, a):
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
        @classmethod
        def create(cls, a: int):
            return cls(a=a)

        def foo(self, a):
            return self.a + a

        def new_foo(self):
            return self.a + 1

    assert Foo.create(3).foo(4) == 3 + 4
    assert Foo(a=5).new_foo() == 5 + 1
    assert Foo().hmm() == 5


def test_plain_abc_multiple():
    class IFoo(PlainABC):
        @classmethod
        @abstractmethod
        def create(cls, *args, **kwargs):
            ...

        @abstractmethod
        def foo(self, a):
            ...

    class INewFoo(PlainABC):
        @abstractmethod
        def new_foo(self):
            ...

    class Foo(ARecord, IFoo, INewFoo):
        @classmethod
        def create(cls, a: int):
            return cls(a=a)

        def foo(self, a):
            return self.a + a

        def new_foo(self):
            return self.a + 1

    assert Foo.create(3).foo(4) == 3 + 4
    assert Foo(a=5).new_foo() == 5 + 1


def test_plain_abc_missing_impl():
    class IFoo(PlainABC):
        @abstractmethod
        def foo(self, a):
            ...

    with pytest.raises(MissingImplError):

        class _(ARecord, IFoo):
            ...


def test_plain_abc_wrong_impl():
    class IFoo(PlainABC):
        @abstractmethod
        def foo(self, a):
            ...

    with pytest.raises(WrongImplError):

        class _(ARecord, IFoo):
            def foo(self, a, b):
                return a + b


def test_plain_abc_conflict():
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

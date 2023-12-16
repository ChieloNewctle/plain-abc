# plain-abc

[![PyPI version](https://img.shields.io/pypi/v/plain-abc.svg)](https://pypi.org/project/plain-abc/)
[![License](https://img.shields.io/github/license/ChieloNewctle/plain-abc)](LICENSE)
[![Build status](https://github.com/ChieloNewctle/plain-abc/actions/workflows/ci.yml/badge.svg)](https://github.com/ChieloNewctle/plain-abc/actions)

Another `ABC` implementation without `metaclass`.

It is a little bit annoying to have `metaclass` conflict,
especially when trying to use ABC along with other libraries.

`plain-abc` provides a simple `ABC` implementation without `metaclass`.

## Installation

```sh
pip install plain-abc
```

## Usage

But you can also use `plain-abc` to solve the problem:

```python
from abc import abstractmethod

from plain_abc import PlainABC


class _SomeHiddenMetaclass(type):
    pass


class Base(metaclass=_SomeHiddenMetaclass):
    pass


class IFoo(PlainABC):
    @abstractmethod
    def foo(self): ...


class Foo(Base, IFoo):
    def foo(self): ...
```

To extend an abstract class **as another abstract class**,
`PlainABC` is required to be one of the bases:

```python
from abc import abstractmethod

from plain_abc import PlainABC


class IEntity(PlainABC):
    @abstractmethod
    def get_id(self) -> str: ...


class IProjectile(IEntity, PlainABC):
    @abstractmethod
    def get_speed(self) -> float: ...


class Arrow(IProjectile):
    def get_id(self) -> str: ...
    def get_speed(self) -> float: ...
```

To skip signature checking,
you can add the member names in `__abc_concrete_members__` of a subclass:

```python
from abc import abstractmethod
from enum import Enum

from plain_abc import PlainABC


class IEnum(PlainABC):
    @property
    @abstractmethod
    def foo(self) -> str:
        ...


class Foo(IEnum, Enum):
    # for python 3.10 or lower
    __abc_concrete_members__ = ('foo',)
    foo = 'foo'


assert Foo.foo.value == 'foo'
```

## To solve `metaclass` conflict without `plain-abc`

Here is an example of `metaclass` conflict
and how to mix `ABCMeta` with other `metaclass`es.

```python
from abc import ABC, ABCMeta, abstractmethod


class _SomeHiddenMetaclass(type):
    ...


class Base(metaclass=_SomeHiddenMetaclass):
    ...


class IFoo(ABC):
    @abstractmethod
    def foo(self): ...


# oh no, metaclass conflict!
# class Foo(Base, IFoo):
#     def foo(self): ...


# create a new metaclass to solve the conflict
class NewMetaclass(_SomeHiddenMetaclass, ABCMeta):
    ...


class Foo(Base, IFoo, metaclass=NewMetaclass):
    def foo(self): ...
```

# plain-abc

An ABC implementation without metaclass.

It is a little bit annoying to have metaclass conflict,
especially when trying to use ABC along with other libraries.

`plain-abc` provides a simple ABC implementation without metaclass.

## Solving metaclass conflict without `plain-abc`

Here is an example of metaclass conflict
and a solution to mix ABCMeta and other metaclasses.

```python
from abc import ABC, ABCMeta, abstractmethod


class _SomeHiddenMetaclass(type):
    pass


class Base(metaclass=_SomeHiddenMetaclass):
    pass


class IFoo(ABC):
    @abstractmethod
    def foo(self): ...


# oh no, metaclass conflict!
# class Foo(Base, IFoo):
#     def foo(self): ...


# create a new metaclass for either IFoo or Foo
class NewMetaclass(_SomeHiddenMetaclass, ABCMeta):
    ...


class Foo(Base, IFoo, metaclass=NewMetaclass):
    def foo(self): ...
```

## Usage

But you can also use `plain-abc` to solve the problem.

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

"""
An ABC implementation without metaclass
better compatibility with other libraries
"""
import sys
from abc import abstractmethod
from inspect import signature
from itertools import dropwhile
from typing import Callable, Iterable, Tuple

if sys.version_info < (3, 8):
    from importlib_metadata import version
else:
    from importlib.metadata import version

__version__ = version('plain-abc')


def is_abstractmethod(f: Callable) -> bool:
    return getattr(f, '__isabstractmethod__', False)


def __sanity_check():
    @abstractmethod
    def f():
        ...

    assert is_abstractmethod(f)

    def g():
        ...

    assert not is_abstractmethod(g)


__sanity_check()


class PlainABCError(Exception):
    pass


class NameConflictError(PlainABCError):
    def __init__(self, name, method, defined, *args, **kwargs):
        self.name, self.method, self.defined = name, method, defined
        message = f'method {name} should be defined only once'
        super().__init__(message, *args, **kwargs)


class WrongImplError(PlainABCError):
    def __init__(self, name, method, defined, *args, **kwargs):
        self.name, self.method, self.defined = name, method, defined
        message = f'wrong implementation for method {name}'
        super().__init__(message, *args, **kwargs)


class MissingImplError(PlainABCError):
    def __init__(self, missing_methods, *args, **kwargs):
        self.missing_methods = tuple(missing_methods)
        method_signatures = ', '.join(
            map(str, map(signature, self.missing_methods[:3]))
        )
        missing_more = '...' if len(missing_methods) > 3 else ''
        message = (
            f'missing implementation for {method_signatures}{missing_more}'
        )
        super().__init__(message, *args, **kwargs)


class PlainABC(object):
    @classmethod
    def _get_abstract_methods(cls) -> Iterable[Tuple[str, Callable]]:
        return (
            (name, attr)
            for tp in dropwhile(lambda x: x != PlainABC, reversed(cls.__mro__))
            for name, attr in tp.__dict__.items()
            if not name.startswith('__') and callable(attr)
        )

    @classmethod
    def __init_subclass__(cls, **kwargs):
        defined, covered = dict(), set()

        for name, method in cls._get_abstract_methods():
            if is_abstractmethod(method):
                if name in defined:
                    raise NameConflictError(name, method, defined[name])
                defined[name] = method
            elif name in defined:
                if signature(method) != signature(defined[name]):
                    raise WrongImplError(name, method, defined[name])
                covered.add(name)

        if PlainABC not in cls.__bases__:
            uncovered = frozenset(defined.keys()).difference(covered)
            if uncovered:
                raise MissingImplError(tuple(map(defined.get, uncovered)))

        return super().__init_subclass__(**kwargs)

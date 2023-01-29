"""
An ABC implementation without metaclass
better compatibility with other libraries
"""
import inspect
import sys
from abc import abstractmethod
from itertools import dropwhile

if sys.version_info < (3, 8):
    from importlib_metadata import version
else:
    from importlib.metadata import version

__version__ = version('plain-abc')


def is_abstractmember(f) -> bool:
    return getattr(f, '__isabstractmethod__', False)


def __sanity_check():
    @abstractmethod
    def f():
        ...

    assert is_abstractmember(f)

    def g():
        ...

    assert not is_abstractmember(g)


__sanity_check()


class PlainABCError(Exception):
    pass


class NameConflictError(PlainABCError):
    def __init__(self, current, pre_defined, *args, **kwargs):
        self.current, self.pre_defined = current, pre_defined
        tp, name, _ = current
        message = f'name conflict in {tp}, abstract member {name} should be defined only once'
        super().__init__(message, *args, **kwargs)


class WrongImplError(PlainABCError):
    def __init__(self, current, pre_defined, *args, **kwargs):
        self.current, self.pre_defined = current, pre_defined
        tp, name, _ = current
        message = f'wrong implementation for member {name} in {tp}'
        super().__init__(message, *args, **kwargs)


class MissingImplError(PlainABCError):
    def __init__(self, cls, missing, *args, **kwargs):
        self.cls, self.missing = cls, tuple(sorted(missing))
        missing_names = ', '.join(self.missing[:3])
        missing_more = '...' if len(self.missing) > 3 else ''
        message = f'missing implementation in {cls} for {missing_names}{missing_more}'
        super().__init__(message, *args, **kwargs)


class PlainABC(object):
    @classmethod
    def _plain_abc_members_to_verify(cls):
        return (
            (tp, name, attr)
            for tp in dropwhile(lambda x: x != PlainABC, reversed(cls.__mro__))
            if issubclass(tp, PlainABC)
            for name, attr in tp.__dict__.items()
        )

    @classmethod
    def _plain_abc_member_signature(cls, name, member):
        if isinstance(member, property):
            return property
        if isinstance(member, (classmethod, staticmethod)):
            return inspect.signature(getattr(cls, name))
        if callable(member):
            return inspect.signature(member)
        raise TypeError(
            f'unknown type of member {name}: {member} to get the signature'
        )

    @classmethod
    def __init_subclass__(cls, **kwargs):
        defined, covered = dict(), set()

        for tp, name, attr in cls._plain_abc_members_to_verify():
            if is_abstractmember(attr):
                if name in defined:
                    raise NameConflictError((tp, name, attr), defined[name])

                defined[name] = tp, name, attr
            elif name in defined:
                defined_tp, _, defined_attr = defined[name]
                defined_signature = defined_tp._plain_abc_member_signature(
                    name, defined_attr
                )

                current_signature = tp._plain_abc_member_signature(name, attr)

                if current_signature != defined_signature:
                    raise WrongImplError((tp, name, attr), defined[name])

                covered.add(name)

        if PlainABC not in cls.__bases__:
            missing = frozenset(defined.keys()).difference(covered)
            if missing:
                raise MissingImplError(cls, missing)

        return super().__init_subclass__(**kwargs)

"""
An ABC implementation without metaclass
better compatibility with other libraries
"""
import inspect
from abc import abstractmethod
from importlib.metadata import version
from itertools import dropwhile

__version__ = version("plain-abc")


def is_abstractmember(f) -> bool:
    return getattr(f, "__isabstractmethod__", False)


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
    @classmethod
    def from_context(cls, current, pre_defined, **kwargs):
        tp, name, _ = current
        message = (
            f"name conflict in {tp}, "
            f"abstract member {name} should be defined only once"
        )
        res = cls(message, **kwargs)
        if hasattr(res, "add_note"):
            res.add_note(f"{pre_defined=}")
        return res


class WrongImplError(PlainABCError):
    @classmethod
    def from_context(cls, current, pre_defined, **kwargs):
        tp, name, _ = current
        message = f"wrong implementation for member {name} in {tp}"
        res = cls(message, **kwargs)
        if hasattr(res, "add_note"):
            res.add_note(f"{pre_defined=}")
        return res


class MissingImplError(PlainABCError):
    @classmethod
    def from_context(cls, clazz, missing, **kwargs):
        missing = tuple(sorted(missing))
        missing_names = ", ".join(missing[:3])
        missing_more = "..." if len(missing) > 3 else ""
        message = f"missing implementation in {clazz} for {missing_names}{missing_more}"
        res = cls(message, **kwargs)
        if missing_more and hasattr(res, "add_note"):
            res.add_note(f"{missing=}")
        return res


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
        # in cases where `property` is callable
        if isinstance(member, property):
            return property

        if isinstance(member, (classmethod, staticmethod)):
            return inspect.signature(getattr(cls, name))

        if callable(member):
            return inspect.signature(member)

        return property

    @classmethod
    def _plain_abc_members_assumed_concrete(cls):
        return frozenset(
            name
            for tp in dropwhile(lambda x: x != PlainABC, reversed(cls.__mro__))
            if issubclass(tp, PlainABC)
            for name in tp.__dict__.get("__abc_concrete_members__", ())
        )

    @classmethod
    def __init_subclass__(cls, **kwargs):
        defined, covered = dict(), set()
        concrete_members = cls._plain_abc_members_assumed_concrete()

        for tp, name, attr in cls._plain_abc_members_to_verify():
            if name in concrete_members:
                continue

            if is_abstractmember(attr):
                if name in defined:
                    raise NameConflictError.from_context(
                        (tp, name, attr), defined[name]
                    )

                defined[name] = tp, name, attr
            elif name in defined:
                defined_tp, _, defined_attr = defined[name]
                defined_signature = defined_tp._plain_abc_member_signature(
                    name, defined_attr
                )

                current_signature = tp._plain_abc_member_signature(name, attr)

                if current_signature != defined_signature:
                    raise WrongImplError.from_context((tp, name, attr), defined[name])

                covered.add(name)

        if PlainABC not in cls.__bases__:
            missing = frozenset(defined.keys()).difference(covered)
            if missing:
                raise MissingImplError.from_context(cls, missing)

        return super().__init_subclass__(**kwargs)

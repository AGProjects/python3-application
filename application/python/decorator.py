
"""Decorators and helper functions for writing well behaved decorators."""

from inspect import signature
from threading import RLock

from application.python.weakref import weakobjectmap

__all__ = 'decorator', 'preserve_signature', 'execute_once'


def decorator(func):
    """A syntactic marker with no other effect than improving readability."""
    return func


def preserve_signature(func):
    """Preserve the original function signature and attributes in decorator wrappers."""
    def fix_signature(wrapper):
        exec_scope = {}
        sig = signature(func)
        parameters = sig.replace(parameters=[parameter.replace(default=parameter.empty) for parameter in sig.parameters.values()])

        exec("def {0}{1}: return wrapper{1}".format(func.__name__, parameters), {'wrapper': wrapper}, exec_scope)  # can't use tuple form here (see https://bugs.python.org/issue21591)
        new_wrapper = exec_scope.pop(func.__name__)
        new_wrapper.__name__ = func.__name__
        new_wrapper.__doc__ = func.__doc__
        new_wrapper.__module__ = func.__module__
        new_wrapper.__defaults__ = func.__defaults__
        new_wrapper.__dict__.update(func.__dict__)
        return new_wrapper
    return fix_signature


@decorator
def execute_once(func):
    """Execute function/method once per function/instance"""

    # noinspection PyUnusedLocal
    @preserve_signature(func)
    def check_arguments(*args, **kw):
        pass

    class ExecuteOnceMethodWrapper(object):
        __slots__ = '__weakref__', '__method__', '__owner__', 'im_func_wrapper'

        def __init__(self, method, owner, func_wrapper):
            self.__method__ = method
            self.__owner__ = owner
            self.im_func_wrapper = func_wrapper

        def __call__(self, *args, **kw):
            with self.im_func_wrapper.lock:
                method = self.__method__
                instance = getattr(method, '__self__', None)
                if instance is not None:
                    check_arguments.__get__(instance, instance.__class__)(*args, **kw)
                else:  # method was accessed via the class (plain function in python3), the instance is expected as the 1st argument
                    check_arguments(*args, **kw)
                    instance = args[0]
                if self.im_func_wrapper.__callmap__.get(instance, False):
                    return
                self.im_func_wrapper.__callmap__[instance] = True
                self.im_func_wrapper.__callmap__[instance.__class__] = True
                return method.__call__(*args, **kw)

        def __dir__(self):
            return sorted(set(dir(self.__method__) + dir(self.__class__) + list(self.__slots__)))

        def __get__(self, obj, cls):
            method = self.__method__.__get__(obj, cls)
            return self.__class__(method, cls, self.im_func_wrapper)

        def __getattr__(self, name):
            return getattr(self.__method__, name)

        def __setattr__(self, name, value):
            if name in self.__slots__:
                object.__setattr__(self, name, value)
            else:
                setattr(self.__method__, name, value)

        def __delattr__(self, name):
            if name in self.__slots__:
                object.__delattr__(self, name)
            else:
                delattr(self.__method__, name)

        def __repr__(self):
            return self.__method__.__repr__().replace('<', '<wrapper of ', 1)

        @property
        def called(self):
            instance = getattr(self.__method__, '__self__', None)
            return self.im_func_wrapper.__callmap__.get(instance if instance is not None else self.__owner__, False)

        @property
        def lock(self):
            return self.im_func_wrapper.lock

    class ExecuteOnceFunctionWrapper(object):
        __slots__ = '__weakref__', '__func__', '__callmap__', 'lock'

        # noinspection PyShadowingNames
        def __init__(self, func):
            self.__func__ = func
            self.__callmap__ = weakobjectmap()
            self.__callmap__[func] = False
            self.lock = RLock()

        def __call__(self, *args, **kw):
            with self.lock:
                check_arguments(*args, **kw)
                if self.__callmap__[self.__func__]:
                    return
                self.__callmap__[self.__func__] = True
                return self.__func__.__call__(*args, **kw)

        def __dir__(self):
            return sorted(set(dir(self.__func__) + dir(self.__class__) + list(self.__slots__)))

        def __get__(self, obj, cls):
            method = self.__func__.__get__(obj, cls)
            return ExecuteOnceMethodWrapper(method, cls, self)

        def __getattr__(self, name):
            return getattr(self.__func__, name)

        def __setattr__(self, name, value):
            if name in self.__slots__:
                object.__setattr__(self, name, value)
            else:
                setattr(self.__func__, name, value)

        def __delattr__(self, name):
            if name in self.__slots__:
                object.__delattr__(self, name)
            else:
                delattr(self.__func__, name)

        def __repr__(self):
            return self.__func__.__repr__().replace('<', '<wrapper of ', 1)

        @property
        def called(self):
            return self.__callmap__[self.__func__]

    return ExecuteOnceFunctionWrapper(func)


__usage__ = """
from application.python.decorator import decorator, preserve_signature

# indicate that the next function will be used as a decorator (optional)
@decorator
def print_args(func):
    @preserve_signature(func)
    def wrapper(*args, **kw):
        print('arguments: args={}, kw={}'.format(args, kw)
        return func(*args, **kw)
    return wrapper

@print_args
def foo(x, y, z=7):
    return x + 3*y + z*z

"""

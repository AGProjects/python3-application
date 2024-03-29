#!/usr/bin/python3

from application.python.types import Singleton


class Unique(object, metaclass=Singleton):
    """This class has only one instance"""


class CustomUnique(object, metaclass=Singleton):
    """This class has one instance per __init__ arguments combination"""

    def __init__(self, name='default', value=1):
        self.name = name
        self.value = value


o1 = Unique()
o2 = Unique()

print("o1 is o2 (expect True):", o1 is o2)

co1 = CustomUnique()
co2 = CustomUnique()
co3 = CustomUnique(name='my name')
co4 = CustomUnique(name='my name')
co5 = CustomUnique(name='my name', value=2)
co6 = CustomUnique(name='my other name')

print("co1 is co2 (expect True):", co1 is co2)
print("co3 is co4 (expect True):", co3 is co4)
print("co1 is co3 (expect False):", co1 is co3)
print("co4 is co5 (expect False):", co4 is co5)
print("co4 is co6 (expect False):", co4 is co6)

import unittest

__all__ = ['TestHelloworld']


class TestHelloworld(unittest.TestCase):

    def test_hello(self):
        self.assertNotEqual('hello', 'world')

    def test_world(self):
        self.assertEqual('hello world'.split(' '), ['hello', 'world'])

# -*- coding: utf-8 -*-

import copy

'''这里定义了一些与 dict 相关的工具函数

模仿 php 构造了这些函数，尽可能的支持 dot 语法'''


def _input_keys(keys):
    '''让函数支持多种参数输入方式，例如以下三种方法获得的参数都是一样的：

        def func(*args): pass
        func(k1, k2)
        func([k1, k2])
        func((k1, k2))
    '''
    if len(keys) == 1 and isinstance(keys[0], (tuple, list)):
        keys = keys[0]
    return keys


def _detect_dict(*args):
    '''检查输入的参数是否 dict 类型'''
    for arg in args:
        if not isinstance(arg, dict):
            raise ValueError("Expected dict type, but type is %s" % type(arg))


def dict_search(items, value, strict=False):
    '''在 dict 中搜索给定的值，如果成功则返回首个相应的 key'''
    _detect_dict(items)

    for (k, v) in items.items():
        if strict and v is value:
            return k
        elif v == value:
            return k

    return False


def dict_get(items, key, default=None):
    '''按 dot key 语法，从 dict 获取 key 对应的值

        d = dict(a=dict(x=1, y=2, z=3))
        dict_get(d, 'a.z') # 3
    '''
    _detect_dict(items)

    result = copy.deepcopy(items)
    for k in key.split('.'):
        if k not in result or not result[k]:
            return default

        result = result.get(k)

    return result


def dict_has(items, key):
    '''按 dot key 语法，判断 key 是否存在

        d = dict(a=dict(x=1))
        dict_has(d, 'a.x') # True
        dict_has(d, 'a.z') # False
    '''
    _detect_dict(items)

    result = copy.deepcopy(items)
    for k in key.split('.'):
        if k not in items:
            return False

        result = items.get(k)

    return True


def dict_set(items, key, value):
    '''按 dot key 语法，从 dict 获取 key 对应的值

        d = dict()
        dict_set(d, 'x.y', 1) # {"x": {"y": 1}}
        dict_set(d, 'x.y', 2) # {"x": {"y": 2}}
    '''
    _detect_dict(items)

    result = copy.deepcopy(items)
    p = key.find('.')
    if p > -1:
        k = key[:p]
        s = result[k] if k in result else {}

        if not isinstance(s, dict):
            raise ValueError('Invalid value setting "%s" => "%s"' % (str(key), str(value)))

        result.update({k: dict_set(s, key[p + 1:], value)})
    else:
        result.update({key: value})

    return result


def dict_pop(items, key, default=None):
    '''按 dot key 语法，从 dict 弹出元素，并获取 key 对应的值

        d = dict(a=dict(x=1, y=2, z=3))
        dict_pop(d, 'a.z') # 3
        print(d)           # {'a': {'x': 1, 'y': 2}}
    '''
    _detect_dict(items)

    def pop_from(items, keys):
        it = keys.pop(0)
        if keys:
            items = items[it]
            return pop_from(items, keys)

        return items.pop(it, default)

    return pop_from(items, key.split('.'))


def dict_only(items, *keys):
    '''仅保留 dict 中指定的 key 值

        d = dict(a=dict(x=1, y=2, z=3))
        dict_only(d,  'a.y', 'a.z')  # {'a': {'x': 1}}
        dict_only(d, ['a.y', 'a.z']) # {'a': {'x': 1}}
        dict_only(d, ('a.y', 'a.z')) # {'a': {'x': 1}}
    '''
    _detect_dict(items)

    result = {}
    for key in _input_keys(keys):
        p = key.find('.')
        k = key[:p] if p > -1 else key

        if p > -1 and isinstance(items[k], dict):
            d = dict_only(items[k], key[p + 1:])
        else:
            d = items[k]

        if k in result:
            result[k].update(d)
        else:
            result[k] = d

    return result


def dict_forget(items, *keys):
    '''按 dot key 语法，从 dict 中移除指定的元素

        d = dict(a=dict(x=1, y=2, z=3))
        dict_forget(d,  'a.x', 'a.y')  # {'a': {'z': 3}}
        dict_forget(d, ['a.x', 'a.y']) # {'a': {'z': 3}}
        dict_forget(d, ('a.x', 'a.y')) # {'a': {'z': 3}}
    '''
    _detect_dict(items)

    result = copy.deepcopy(items)
    for key in _input_keys(keys):
        dict_pop(result, key)

    return result


def dict_merge(*dicts):
    '''合并多个 dict'''
    _detect_dict(*dicts)

    result = {}
    for d in dicts:
        result.update(d)

    return result


def dict_merge_recursive(source, dest):
    '''递归深度合并两个 dict

        # 以下结果为 {'a': {'x': 1, 'y': 2}}
        dict_merge_recursive(dict(a=dict(x=1)), dict(a=dict(y=2)))
    '''
    _detect_dict(source, dest)

    import collections

    result = copy.deepcopy(source)
    for k, v in dest.items():
        if k in result and isinstance(result[k], dict) \
                and isinstance(dest[k], collections.Mapping):
            result[k] = dict_merge_recursive(result[k], dest[k])
        else:
            result[k] = dest[k]

    return result


def dict_depth(items):
    '''计算 dict 的深度(维数)

        dict_depth({})              # 0
        dict_depth({"x": 1})        # 1
        dict_depth({"x": {"y": 2}}) # 2
    '''
    _detect_dict(items)

    def depth(d, n):
        if not isinstance(d, dict) or not d:
            return n

        return max(depth(v, n + 1) for k, v in d.items())

    return depth(items, 0)

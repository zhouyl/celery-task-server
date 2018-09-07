# -*- coding: utf-8 -*-

import socket
from helpers import *
from utils import logger
from redis import Redis
from thrift.Thrift import TException, TApplicationException
from thrift.transport.TSocket import TSocket
from thrift.transport.TTransport import TFramedTransport
from thrift.protocol.TBinaryProtocol import TBinaryProtocol
from thrift.transport.TTransport import TTransportException

sys.path.append(root_path('thrifts/security'))

from security import SecurityService
from security.ttypes import ResultStruct

REDIS_NS = 'FORMAX_SECURITY_NS'


class ConnectFailed(Exception):
    '''创建连接失败'''


class SecurityClient(object):
    '''加解密服务客户端

        s = SecurityClient(**config('security'), redis=redis.Redis())

        s.encrypt(["18603038502", "18603038501"])
        #  {'18603038502': 'WNOs5ERgD4LnXoS/TFJsvw==', '18603038501': '2jjjfgeFUV8sMeDRoj/O+Q=='}

        s.encrypt(["18603038502", "18603038501"], False)
        #  {'18603038502': '24NxoOquR+MBers9R22CIg==', '18603038501': '64ng3g5S4swfCI0m2Mb3IQ=='}

        s.encrypt(['18603038502'])
        #  {'18603038502': 'WNOs5ERgD4LnXoS/TFJsvw=='}

        s.encrypt('18603038502')
        #  WNOs5ERgD4LnXoS/TFJsvw==

        s.decrypt(['WNOs5ERgD4LnXoS/TFJsvw==', '24NxoOquR+MBers9R22CIg=='])
        #  {'WNOs5ERgD4LnXoS/TFJsvw==': '18603038502', '24NxoOquR+MBers9R22CIg==': '18603038502'}

        s.decrypt(['WNOs5ERgD4LnXoS/TFJsvw=='])
        #  {'WNOs5ERgD4LnXoS/TFJsvw==': '18603038502'}

        s.decrypt('WNOs5ERgD4LnXoS/TFJsvw==')
        #  18603038502
    '''

    _client = None
    _sock = None

    def __init__(self, host, port, timeout=3, redis=None, maxtries=3):
        if redis and not isinstance(redis, Redis):
            raise ValueError("<redis> argument must be instance of %s" % Redis)

        self._host = str(host)
        self._port = int(port)
        self._timeout = int(timeout)
        self._redis = redis
        self._maxtries = int(maxtries)
        self._logger = logger.get(__name__)

    def _socket(self):
        '''打开一个 socket 连接'''
        if self._sock:
            return self._sock

        for i in range(self._maxtries):
            try:
                self._sock = TSocket(self._host, self._port)
                if not self._sock:
                    raise ConnectFailed('Create TSocket failed')

                if self._timeout:
                    self._sock.setTimeout(self._timeout * 1000)

                self._sock.open()

                return self._sock
            except TTransportException as e:
                self._logger.error('Connect failed [%d tries]: <%s> %s',
                                   i, e.__class__.__name__, e)

                if i > (self._maxtries - 2):
                    raise e
                else:
                    time.sleep(0.1)  # 休息一下，再重试打开 socket

    def connect(self):
        '''尝试连接到 thrift server'''
        if not self._client:
            self._client = SecurityService.Client(
                TBinaryProtocol(TFramedTransport(self._socket())))

            self._logger.debug('Thrift client connect successfully.')

        return self._client

    def close(self):
        '''关闭连接'''
        self._client = None
        if self._sock:
            self._sock.close()
            self._sock = None

        self._logger.debug('Thrift client was closed.')

    def encrypt(self, texts, ecb=True):
        '''对单个或多个字符进行加密处理'''
        texts = self._convert(texts)

        if not texts:
            return False

        if isinstance(texts, str):
            return self._encrypt_with_redis(texts, ecb) or self._single_encrypt(texts, ecb)

        results = self._batch_encrypt_with_redis(texts, ecb)
        fails = {k: v for k, v in results.items() if not v}

        if fails:
            # 将从缓存查询失败的字符，通过 thrift 进行查询
            results.update(self._batch_encrypt(list(fails.keys()), ecb))

        return results

    def decrypt(self, texts):
        '''对单个或多个字符进行解密处理'''
        texts = self._convert(texts)

        if not texts:
            return False

        if isinstance(texts, str):
            return self._decrypt_with_redis(texts) or self._single_decrypt(texts)

        results = self._batch_decrypt_with_redis(texts)
        fails = {k: v for k, v in results.items() if not v}

        if fails:
            # 将从缓存查询失败的字符，通过 thrift 进行查询
            results.update(self._batch_decrypt(list(fails.keys())))

        return results

    def _convert(self, texts):
        '''转换输入的文本参数数据，支持 str/list/tuple/dict 输入'''
        if not isinstance(texts, (str, list, tuple, dict)):
            raise ValueError("Invalid encrypt/decrypt source data")

        if isinstance(texts, dict):
            texts = list(texts.values())

        if isinstance(texts, (list, tuple)):
            # 过滤 ''/False/None
            return list(filter(bool, texts))

        return str(texts)

    def _redis_key(self, method, text, ecb):
        '''根据参数，生成 redis key (method 参数可选项为 encrypt/decrypt)'''
        return '%s:%s:%s' % (method, 'ECB' if ecb else 'CBC', text)

    def _redis_get(self, key):
        '''尝试从 redis 中获取数据'''
        if not self._redis:
            return False

        value = self._redis.hget(REDIS_NS, key)
        if value:
            value = value.decode('utf8')
            self._logger.debug('Hit cache: %s => %s', key, value)
            return value

        return False

    def _redis_set(self, key, value):
        '''将数据写入到 redis'''
        if self._redis and len(key) < 1000 and value not in [False, None]:
            self._redis.hset(REDIS_NS, key, value)
            self._logger.debug("Cache set: %s => %s", key, value)

        return value

    def _request(self, method, texts):
        '''向 thrift server 发送处理请求'''
        client = self.connect()

        if isinstance(texts, (list, tuple)):
            texts = dict(zip(texts, texts))

        try:
            # 当遇到连接超时时，尝试重新连接
            for i in range(self._maxtries):
                try:
                    res = getattr(client, method)(texts)
                except (socket.timeout, EOFError, TApplicationException) as e:
                    self._logger.error('Request [%s:%s] failed [%d tries]: %s %s',
                                       method, texts, i, type(e), str(e))
                    if i > (self._maxtries - 2):
                        raise e  # 超过重试限制，抛出异常
                    else:
                        time.sleep(i + 0.1)  # 休息一下，再重试
                else:
                    self._logger.debug('Request [%s:%s] => %s', method, texts, res)
                    break

            # 返回的是单个结果
            if isinstance(res, ResultStruct):
                return res.str if res.err == 0 else False

            # 返回的是一个 dict
            results = {}
            for (k, r) in res.items():
                results[k] = r.str if r.err == 0 else False

            return results
        except UnicodeDecodeError:
            # 通常这种错误是由于 cbc/ecb 解密时的兼容问题造成的
            return False
        except BaseException as e:
            self._logger.error('Request [%s:%s] failed: %s %s',
                               method, texts, type(e), str(e))

            # 当请求失败时，关闭连接以待下次自动重连
            if isinstance(e, TException):
                time.sleep(0.1)
                self.close()

            return False

    def _single_encrypt(self, text, ecb):
        '''执行单个字符的加密'''
        res = self._request('encryptUseEcbModel' if ecb else 'encryptAndBase64', text)

        self._redis_set(self._redis_key('encrypt', text, ecb), res)

        return res

    def _encrypt_with_redis(self, text, ecb):
        '''尝试通过 redis 执行加密'''
        return self._redis_get(self._redis_key('encrypt', text, ecb))

    def _batch_encrypt(self, texts, ecb):
        '''批量对字符进行加密'''
        method = 'batchEncryptUseEcbModel' if ecb else 'batchEncryptAndBase64'

        results = self._request(method, texts)
        for (k, v) in results.items():
            self._redis_set(self._redis_key('encrypt', k, ecb), v)

        return results

    def _batch_encrypt_with_redis(self, texts, ecb):
        '''批量通过 redis 执行加密'''
        return dict(zip(texts, [self._encrypt_with_redis(t, ecb) for t in texts]))

    def _single_decrypt(self, text):
        '''执行单个字符的解密，先尝试 CBC 模式，再尝试 ECB 模式'''
        for m in ('decryptAndBase64', 'decryptUseEcbModel'):
            res = self._request(m, text)
            if res:
                self._redis_set(
                    self._redis_key('decrypt', text, m.endswith('EcbModel')), res)
                return res

        return False

    def _decrypt_with_redis(self, text):
        '''尝试通过 redis 执行加密'''
        return self._redis_get(self._redis_key('decrypt', text, False)) \
            or self._redis_get(self._redis_key('decrypt', text, True))

    def _batch_decrypt(self, texts):
        '''批量对字符进行解密'''

        def _decrypt(texts, ecb):
            method = 'batchDecryptUseEcbModel' if ecb else 'batchDecryptAndBase64'

            results = self._request(method, texts)
            for (k, v) in results.items():
                self._redis_set(self._redis_key('decrypt', k, ecb), v)

            return results

        results = _decrypt(texts, False)  # CBC 解密
        fails = {k: v for k, v in results.items() if not v}

        if fails:
            results.update(_decrypt(list(fails.keys()), True))  # ECB 解密

        return results

    def _batch_decrypt_with_redis(self, texts):
        '''批量通过 redis 执行解密'''
        return dict(zip(texts, [self._decrypt_with_redis(t) for t in texts]))

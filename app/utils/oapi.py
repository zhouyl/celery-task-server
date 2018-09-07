# -*- coding: utf-8 -*-

import requests
import arrow

from helpers.dictionary import dict_get
from . import logger
from simplejson.errors import JSONDecodeError

# 激活 logger 配置，使其能应用于 request & urllib3
logger.apply_config()


class RequestError(RuntimeError):
    pass


class Result(object):

    def __init__(self, code=200, message='', data=None, timestamp=None):
        self.code = code
        self.message = message
        self.data = data
        self.timestamp = arrow.get(timestamp)

    def success(self):
        return self.code == 200

    def failed(self):
        return not self.success()

    def dot(self, key, default=None):
        return dict_get(self.data, key, default) if isinstance(self.data, dict) else default

    @property
    def raw(self):
        return {
            'code': self.code,
            'message': self.message,
            'data': self.data,
            'timestamp': self.timestamp.timestamp
        }


class ErrorResult(Result):

    def __init__(self, message=''):
        super(ErrorResult, self).__init__(code=500, message=message)


class OApiClient(object):

    _log = logger.get(__name__)

    _options = dict(gateway='https://api.my-host.com/api',
                    appId='CRM',
                    appKey='XXXXX',
                    timeout=3,
                    headers={'Host': 'api.my-host.com'},
                    verify=False)

    def __init__(self, **kwargs):
        import urllib3
        from requests.adapters import HTTPAdapter

        self._options.update(kwargs)

        # 当关闭 ssl 验证时，需要关闭掉 urllib3 的警告信息
        # @link https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
        if not self._options['verify'] and self._options['gateway'].startswith('https'):
            urllib3.disable_warnings()

        # 设置 request 自动重试
        s = requests.Session()
        r = urllib3.util.Retry(total=3, status_forcelist=[408, 508])
        s.mount('http://', HTTPAdapter(max_retries=r))
        s.mount('https://', HTTPAdapter(max_retries=r))

    def request(self, api, post=None, headers=None):
        '''请求 oapi 接口'''
        if post is None:
            post = {}

        if headers is None:
            headers = {}

        post.update({'appId': self._options['appId'],
                     'appKey': self._options['appKey'],
                     'operator': 71})

        headers.update(self._options['headers'])

        kwargs = dict(url='{0}/{1}'.format(self._options['gateway'], api),
                      data=post,
                      headers=headers,
                      timeout=self._options['timeout'],
                      verify=self._options['verify'])

        try:
            self._log.info("Request as cURL: %s", self._request_as_curl(kwargs))
            r = requests.post(**kwargs)

            self._log.info("Response: %s", r.content.decode('utf8'))

            return Result(**r.json())
        except JSONDecodeError:
            self._log.warning('JSON decode failed: %s', r.content.decode('utf8'))

            return ErrorResult('JSON decode failed')
        except BaseException as err:
            self._log.warning('Request failed: %s', err)
            return ErrorResult("Request failed: %s" % err)

    def _request_as_curl(self, d):
        '''将请求转换为 curl 格式，以方便调试'''
        parts = ["curl '%s'" % d['url']]

        if d['url'].startswith('https') and d['verify']:
            parts.append('-k')

        if d['data']:
            parts.append("-d '%s'" % '&'.join(['%s=%s' % (k, v) for (k, v) in d['data'].items()]))

        if d['headers']:
            parts.append(' '.join("-H '%s: %s'" % (k, v) for (k, v) in d['headers'].items()))

        if d['timeout']:
            parts.append('--connect-timeout %d' % d['timeout'])

        return ' '.join(parts)

# -*- coding: utf-8 -*-

from helpers import *
from providers import di
from utils import logger


class UNIT(object):
    '''定义业务来源事业部'''

    UNKNOW = 0  # 未知|默认渠道
    SECURITY = 1  # 证券
    WEALTH = 2  # 财富
    CREDIT = 3  # 消金

    # 业务渠道对应业务来源关系
    MAPS = {
        UNKNOW: '未知',
        SECURITY: '证券事业部',
        WEALTH: '财富事业部',
        CREDIT: '消金事业部'
    }


class BUSINESS(object):
    '''定义业务渠道参数'''

    JRQ = -1
    FOREX = 1
    FORBAG = 2
    COLLECT = 4
    FUND = 6
    LIFE = 8
    INSURANCE = 9
    CREDIT = 10
    FX_APP = 12

    # 关键字对应表|业务名
    MAPS = {
        JRQ: 'jrq',
        FOREX: 'forex',
        FORBAG: 'forbag',
        COLLECT: 'collect',
        FUND: 'fund',
        LIFE: 'life',
        INSURANCE: 'insurance',
        CREDIT: 'credit',
        FX_APP: 'forex',  # 证券 app 的来源，被默认为外汇业务
    }

    # 关键字对应业务渠道名称
    PLATFORMS = {
        JRQ: '官网',
        FOREX: '外汇',
        FORBAG: '港美股',
        COLLECT: '集合理财',
        FUND: '基金',
        LIFE: 'LIFE',
        INSURANCE: '保险',
        CREDIT: '福麦信用',
        FX_APP: '证券APP',
    }

    # 业务渠道对应业务来源关系
    UNITS = {
        UNIT.UNKNOW: [],
        UNIT.SECURITY: [FOREX, FORBAG, FX_APP],
        UNIT.WEALTH: [JRQ, COLLECT, FUND, INSURANCE],
        UNIT.CREDIT: [LIFE, CREDIT],
    }


class Business(BUSINESS):

    '''提供业务渠道查询提供相关的方法'''

    @staticmethod
    def key(business):
        '''根据指定的业务值(business_v)，获取对应的表|业务名'''
        if isinstance(business, str):
            lower = business.lower()
            return lower if lower in BUSINESS.MAPS.values() else None

        return BUSINESS.MAPS[business]

    @staticmethod
    def platform(business):
        '''根据指定的业务值(business_v)，获取对应的业务渠道名称'''
        if not is_numeric(business):
            business = dict_search(BUSINESS.MAPS, business)

        # 当获取一个不存在的业务渠道时，默认视为 JRQ
        if business not in BUSINESS.PLATFORMS:
            # 写入一个警告日志，以便及时发现新增加的业务渠道
            logger.get('business-warning') \
                .warning("Attempt to query a non-existent business value %s", business)

            business = BUSINESS.JRQ

        return BUSINESS.PLATFORMS[business]

    @staticmethod
    def unit(business):
        '''根据业务渠道，判断事业部归属'''
        if not is_numeric(business):
            business = dict_search(BUSINESS.MAPS, business)

        for (k, v) in BUSINESS.UNITS.items():
            if business in v:
                return k

        return UNIT.UNKNOW

    @classmethod
    def is_ours(cls, business, unit=UNIT.SECURITY):
        '''判断是否证券事业部的业务渠道'''
        return cls.unit(business) is unit


REFERS_KEY = 'PYSC_DCENTER_REFERS'
CHANNELS_KEY = 'PYSC_DCENTER_CHANNELS'


class Refer(object):

    '''用于处理平台数据中心的 refer id 数据'''

    # 官网默认 ID
    DEFAULT_REFID = 'f7a5678e'

    # 缓存所有的 refer 数据
    __refers = None

    # 缓存所有的渠道数据
    __channels = None

    # 缓存所有的渠道反查数据
    __lookups = {}

    @classmethod
    def fetch_refers(cls):
        '''从数据库查询所有的 refer 数据'''
        items = di['db'].connection('bar').fetch_all(
            '''select
                id, refer_id, refer_str, refer_value, name, channel_id,
                business_v, platform_type, comments, status
            from refer_info''')

        refers = dict(map(lambda item: (item['refer_id'], item), items))

        # 仅缓存 5 分钟，时间太长，影响数据同步
        di['memcache'].set(REFERS_KEY, refers, time=300)

        return refers

    @classmethod
    def refers(cls):
        '''从缓存中获取所有的 refer 数据'''
        if not cls.__refers:
            refers = di['memcache'].get(REFERS_KEY)
            if not refers:
                refers = cls.fetch_refers()

            # 在内部缓存一下
            cls.__refers = refers

        return cls.__refers

    @classmethod
    def refer(cls, refid, default=None):
        '''根据 refid，获取 refer 数据'''
        return cls.refers().get(refid, default)

    @classmethod
    def fetch_channels(cls):
        '''从数据库查询所有的渠道数据'''
        items = di['db'].connection('bar').fetch_all(
            'select id, name from channel')

        channels = dict(map(lambda item: (item['id'], item['name']), items))

        # 仅缓存 5 分钟，时间太长，影响数据同步
        di['memcache'].set(CHANNELS_KEY, channels, time=300)

        return channels

    @classmethod
    def channels(cls, ):
        '''从缓存中获取所有的渠道数据'''
        if not cls.__channels:
            channels = di['memcache'].get(CHANNELS_KEY)
            if not channels:
                channels = cls.fetch_channels()

            # 在内部缓存一下
            cls.__channels = channels

        return cls.__channels

    @classmethod
    def channel(cls, channel_id, default=None):
        '''根据渠道 id，获取渠道名称'''
        return cls.channels().get(channel_id, default)

    @classmethod
    def platform(cls, business, channel_id):
        '''根据业务类型，渠道 id，获取业务渠道名称'''
        if business == 5 or (business == BUSINESS.COLLECT and channel_id == 1):
            # 历史原因，sub_platform = 5 是个错误的用法，应当归到官网
            # 金融圈官网注册的客户，被放到了集合理财的来源中，因此需要特殊对待
            business = BUSINESS.JRQ

        return Business.platform(business)

    @classmethod
    def lookup(cls, **kw):
        '''根据传入的参数，反向查询获得 refer 数据

        该方法主要为兼容没有 refid 数据的注册用户，以获得一个默认的 refid'''
        platform = force_int(kw.get('platform') or kw.get('sub_platform'))
        channel = force_int(kw.get('channel') or kw.get('market_channel'))
        source = force_int(kw.get('source') or kw.get('source_type'))

        # business_v: 1:forex/2:forbag/4:wealth/6:fund/8:life/9:insurance/10:credit/12:fx_app
        # sub_platform: 0:jrq/1:forex/2:forbag/3:wealth/4:p2p/5:mobile/6:fund
        # p2p & jrq 需要归纳到 wealth 里面
        if platform in [0, 3]:
            platform = 4

        # 历史原因，sub_platform=5是个错误的用法，应当归到官网
        elif platform == 5:
            platform = 0

        # source_type: 1:ios/2:android/3:pc/4:ios_ent/5:h5
        # platform_type: 1:ios/2:android/3:pc/4:ios_ent/5:h5
        if source == 0:
            source = 3

        CACHE_ID = "%s.%s.%s" % (platform, channel, source)
        if CACHE_ID not in cls.__lookups:
            cls.__lookups[CACHE_ID] = None

            # sub_platform => business_v
            # platform_type => source_type
            # refer_value => market_channel
            for r in cls.refers().values():
                if int(r['business_v']) == platform and \
                        int(r['platform_type']) == source and \
                        int(r['refer_value']) == channel:
                    cls.__lookups[CACHE_ID] = r
                    break

        return cls.__lookups[CACHE_ID]

    @classmethod
    def unit(cls, refer):
        '''根据 refer 数据或者 refid，判断所属事业部'''
        if isinstance(refer, str):
            refer = cls.refer(refer)  # 传入的可能是 refid

        if not isinstance(refer, dict):
            business = BUSINESS.JRQ
        else:
            business = refer.get('business_v', BUSINESS.JRQ)

        # channel_id == 1，被视为集团官网
        if business == BUSINESS.COLLECT and refer.get('channel_id') == 1:
            business = BUSINESS.JRQ

        return Business.unit(business)

    @classmethod
    def is_ours(cls, refer, unit=UNIT.SECURITY):
        '''根据 refer 数据或者 refid，判断是否证券事业部客户'''
        return cls.unit(refer) is unit

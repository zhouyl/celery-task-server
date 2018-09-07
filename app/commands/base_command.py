# -*- coding: utf-8 -*-

import threading
import queue
import signal
import time
import sys

from utils import logger
from cleo import Command


class BaseCommand(Command):

    # 日志记录器
    log = logger.get('commands')

    # 当前脚本是否停止
    stopped = False

    # 当前脚本是否睡眠中
    slept = False

    def execute(self, i, o):
        signal.signal(signal.SIGINT, self.signal_handle)
        signal.signal(signal.SIGTERM, self.signal_handle)

        self.handle()

    def handle(self):
        raise NotImplementedError

    def signal_handle(self, signum, frame):
        '''用于捕获 SIGINT & SIGTERM 信号，来停止当前脚本'''
        self.log.warning('Catch the signl [%d], script will be stopped ...', signum)

        self.exit()

    def sleep(self, seconds):
        self.slept = True
        time.sleep(seconds)
        self.slept = False

    def exit(self):
        self.stopped = True

        # 当前脚本睡眠中，直接强制退出
        if self.slept:
            self.log.info("This script was slept, force stopped!")
            sys.exit()
        else:
            self.log.info('This script stopped!')


class MultiThreadsCommand(BaseCommand):

    # 线程池
    threads = []

    # 是否通知线程停止
    stopped = False

    def handle(self):
        '''脚本从这里开始执行'''

        # 线程池
        self.threads = self.init_threads()

        # 启动处理线程
        for t in self.threads:
            t.start()

    def init_threads(self):
        '''返回一个 threads list'''
        raise NotImplementedError

    def exit(self):
        '''退出当前脚本，关闭所有的线程'''
        self.stopped = True

        # 阻塞等待
        for t in self.threads:
            t.join()

        self.log.debug('All threads join completed, this script stopped!')


class MultiThreadsQueueCommand(MultiThreadsCommand):

    # 任务结果异步队列
    queue = queue.Queue()

    # 队列锁
    queue_lock = threading.Lock()

    def init_threads(self):
        '''返回一个 threads list'''
        raise NotImplementedError

    def async_queue_thread(self):
        '''异步处理结果线程

        用于处理已完成的结果，并在日志中进行记录'''

        # 等待一下任务处理完毕，避免重新加入队列
        time.sleep(1)

        while True:
            job = self.queue.get(block=True)
            self.log.info("Process job in the queue: %s", str(job))

            self.process_queue(job)

            # 进程已停止，且队列已空
            if self.stopped and self.queue.empty():
                self.log.info('The queue thread stopped!')
                break

    def process_queue(self, job):
        '''处理一条队列中的任务'''
        raise NotImplementedError

    def put_queue(self, job):
        '''写入一个异步结果到队列'''
        self.queue_lock.acquire()
        self.queue.put(job)
        self.queue_lock.release()


class StopError(RuntimeError):
    '''用于辅助来停止当前操作'''
    pass

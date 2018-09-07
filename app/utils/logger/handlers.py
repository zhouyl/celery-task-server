# -*- coding: utf-8 -*-

import os
import time
import smtplib
import psutil
import logging

from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header
from helpers.common import *


class NamedFileHandler(logging.FileHandler):
    '''支持按指定的格式指定 filename

    在 filename 中，可以使用以下参数：

        {root}  - 本项目的根路径
        {name}  - logger 名称
        {year}  - 年份，格式：YYYY
        {month} - 月份，格式：MM
        {date}  - 日期，格式: DD
        {hour}  - 小时，格式: HH
    '''

    def __init__(self, filename, mode='a', encoding=None):
        logging.FileHandler.__init__(self, filename, mode, encoding, delay=True)
        self.sourceFilename = filename
        self.stream_name = None

    def emit(self, record):
        self._namedByFormat(record)

        logging.FileHandler.emit(self, record)

    def _namedByFormat(self, record):
        if self.stream_name == record.name:
            return

        if self.stream:
            self.stream.close()
            self.stream = None

        self.stream_name = record.name
        self.baseFilename = self._formatFilename(record.name, self.sourceFilename)
        self.stream = self._open()

    def _formatFilename(self, name, filename):
        now = datetime.now(TZINFO)

        patterns = {
            '{name}': name,
            '{year}': now.strftime('%Y'),
            '{month}': now.strftime('%m'),
            '{date}': now.strftime('%d'),
            '{hour}': now.strftime('%H'),
        }

        for (k, v) in patterns.items():
            filename = filename.replace(k, v)

        logpath = os.path.dirname(filename)
        if not os.path.isdir(logpath):
            makedirs_ignore_error(logpath)

        return filename


class SMTPHandler(logging.Handler):
    '''python 内置的 logging.handlers.SMTPHandler 存在许多的问题：

    1、每一条 message 会发送一条报警邮件
    2、邮件发送存在编码错误的问题
    3、smtp 无法指定 sender name

    重构改进后的 SMTPHandler 新增了邮件发送延时参数：

        delay: 10 # 当前消息与上一条消息间隔时间 >= 10 秒，则立即发送邮件
        max_records: 100 # 当消息超过 100 条时，立即发送邮件
    '''

    records = {}

    def __init__(self, mailhost, sender, receivers, subject,
                 credentials=None, secure=None, delay=10, max_records=100):
        logging.Handler.__init__(self)

        if isinstance(mailhost, (list, tuple)):
            self.mailhost, self.mailport = mailhost
        else:
            self.mailhost, self.mailport = mailhost, None

        if isinstance(credentials, (list, tuple)):
            self.username, self.password = credentials
        else:
            self.username = None

        if isinstance(receivers, str):
            receivers = [receivers]

        if isinstance(sender, (list, tuple)):
            self.fromaddr, self.fromname = sender
        else:
            self.fromaddr, self.fromname = sender, sender.split('@')[0]

        self.receivers = receivers
        self.subject = subject
        self.secure = secure
        self._timeout = 5.0
        self.delay = delay
        self.max_records = max_records

    def emit(self, record):
        self.records[time.time()] = self.format(record)
        self._send()

    def _sendmail(self):
        if not self.records:
            return False

        try:
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT

            smtp = smtplib.SMTP(self.mailhost, port, timeout=self._timeout)

            if self.username:
                if self.secure is not None:
                    smtp.ehlo()
                    smtp.starttls(*self.secure)
                    smtp.ehlo()

                smtp.login(self.username, self.password)

            # 获取当前进程信息
            pid = os.getpid()
            process = psutil.Process(pid)
            created_at = datetime.fromtimestamp(process.create_time()).strftime(DATETIME_FORMAT)

            # 消息内容初始化
            content = 'pid: %d, cwd: %s, cmd: %s, time: %s\r\n%s\r\n' % \
                (pid, ROOT_PATH, ' '.join(process.cmdline()), created_at, '-' * 80)

            # 使用按 key 排序，以保持消息的时间顺序
            for k in sorted(self.records.keys()):
                content += '\r\n' + self.records[k]

            message = MIMEText(content, 'plain', 'utf-8')
            message['From'] = Header('%s <%s>' % (self.fromname, self.fromaddr), 'utf-8')
            message['To'] = Header(",".join(self.receivers), 'utf-8')
            message['Subject'] = Header(self.subject, 'utf-8')

            smtp.sendmail(self.fromaddr, self.receivers, message.as_string())
            smtp.quit()

            self.records = {}

        except (KeyboardInterrupt, SystemExit):
            raise

    def _send(self, force=False):
        # 如果无延时设置，或者达到最大记录数，或者强制发送时，立即发送邮件
        if self.delay == 0 or force or len(self.records) >= self.max_records:
            self._sendmail()

        # 如果当前消息的时间，距离最近一条消息超过延时时间，则立即发送
        elif len(self.records) > 1:
            times = list(self.records.keys())[-2:]
            if (times[0] - times[1]) >= self.delay:
                self._sendmail()

    def close(self):
        self._send(True)

        logging.Handler.close(self)

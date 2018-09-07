# -*- coding: utf-8 -*-

import os

from cleo import Command
from stringutils import pascal_case, snake_case
from helpers.common import app_path


COMMAND_STUBS = r"""# -*- coding: utf-8 -*-

from .base_command import BaseCommand


class {0}(BaseCommand):

    '''
    The commmand description

    {1}
        {{argument : The argument set of the command.}}
        {{--o|option= : The option set of the command.}}
    '''

    def handle(self):
        pass
"""


class MakeCommand(Command):

    '''
    Create a new command.

    make:command
        {name : The name of the command.}
        {--command= : The terminal command that should be assigned.}
        {--p|path= : The path to commands files.}
    '''

    def handle(self):
        name = self.argument('name')
        class_name = pascal_case(name) + 'Command'
        stub = COMMAND_STUBS.format(class_name, self.option('command') or name)

        path = self.option('path')
        if path is None:
            path = app_path('commands')

        filepath = '{}/{}_command.py'.format(path, snake_case(name))

        if os.path.exists(filepath):
            raise RuntimeError('The command file already exists.')

        with open(filepath, 'w') as f:
            f.write(stub)

        self.line('Command <comment>%s</> successfully created.' % class_name)

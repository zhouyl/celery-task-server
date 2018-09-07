# 证券事业部数据处理服务

当前项目使用的是 `python 3.5`，如果你不清楚其与 `2.7` 版本的差异，可以参考这里：https://blog.csdn.net/samxx8/article/details/21535901

## 一、环境配置

建议使用 `vscode` 环境开发本项目。在 `.vscode` 目录中，已经做好了 `autopep8` 自动格式化以及 `python debug` 环境的配置

### 1、安装 virtualenv

```shell
$ sudo apt-get install python3-pip
$ pip3 install virtualenv
$ cd /workspace/sc-data-center
$ virtualenv --no-site-packages -p /usr/bin/python3 venv
```

### 2、包管理

导入依赖包

```shell
$ venv/bin/pip install --upgrade pip # 升级 pip
$ venv/bin/pip install -r requirements.txt
$ venv/bin/pip install -r requirements_dev.txt # 开发环境使用这个
```

如果在后续开发过程中，有新增依赖包，请运行更新命令

```bash
$ venv/bin/pip freeze > requirements.txt
```

### 3、选择使用 pyenv

也可以选择使用 pyenv 来替代管理 virtualenv，会更便捷，但可能会出现像我一样遇到的问题：无法检测到系统已安装的 lib

 ```shell
 $ sudo apt-get install pyenv
 $ pyenv install 3.5.5rc1
 ```

添加到 ~/.bash_profile 末尾

```shell
export PYENV_ROOT="${HOME}/.pyenv"

if [ -d "${PYENV_ROOT}" ]; then
  export PATH="${PYENV_ROOT}/bin:${PATH}"
  eval "$(pyenv init -)"
  eval "$(pyenv virtualenv-init -)"
fi
```

刷新 path
```shell
$ pyenv rehash
$ source ~/.bash_profile
```

安装项目
```shell
$ cd /workspace/celery-task-server
$ echo 'celery-task-server' > .python-version
$ pyenv virtualenv 3.5.5rc1 celery-task-server
$ cd -
$ cd /workspace/celery-task-server # 重新进入该目录，将自动激活 python 版本环境
$ python --version # 查看 python 版本
$ pip install -r requirements_dev.txt
```

## 二、包使用说明&参考文档

该项目中应用到了一些重要的包，这些包提供了不同的项目功能支持。为了兼顾 php 的开发习惯，同时在项目中引入了一些与 php 类似的包。

如果某些包无法查看参考文档（可能因为墙的原因），建议直接通过参考 `venv/lib/python3.5/site-packages` 下的包源代码来学习使用这些包。

### `celery`

这是本项目最重要的一个包，提供任务调度功能，相关帮助信息请参考：http://docs.celeryproject.org/en/latest/index.html

`app/tasks` 目录用于存放 celery 所有的 tasks！

### `var_dump`

这个包提供了像 php var_dump 一样的功能，但在调试比较大的对象时，可能会导出溢出操作，慎重！

```python
from var_dump import var_dump
from var_dump import var_export

d = dict(x=1, y=2)

var_dump(d)
'''
#0 dict(2)
    ['y'] => int(2)
    ['x'] => int(1)
'''

print(var_export(d))
'''
#0 dict(2)     ['y'] => int(2)     ['x'] => int(1)
'''
```

### `arrow`

这是目前 python 中最好用的日期时间处理包，参考文档见：http://arrow.readthedocs.io/

**注意：**

在输出日期时间字符时，记得加上 `to(CONST.TZ)`，例如：`arrow.Arrow.fromtimestamp(1524641352).to('Asia/Shanghai').format()`

### `pendulum`

这是一个仿 php [Carbon](https://github.com/briannesbitt/Carbon) 的包，参考文档地址：https://pendulum.eustace.io/docs/

**注意：**

你可以使用这个类来做一些日期时间的计算，但需要注意的是，这个类的时区并不准！
因为当你使用 `pendulum.now().set(tz='Asia/Shanghai').format('%Y-%m-%d %H:%M:%S %z')` 输出当前时间时会发现，这并不是一个正确的时间！你应该使用 `arrow` 这个日期时间包！

### `cleo`

这也是一个跟目前 laravel/symfony 框架中 Command 类似的一个包，可以直接查看项目中的示例来熟悉这个包。参考文档地址：http://cleo.readthedocs.io

### `orator`

这个包完全模仿了 laravel database & eloquent，大部分的使用方法都是类似的。同时，这个包集成了 `cleo`，并提供了许多与 laravel 相同的 make 功能，代码位置在 `venv/lib/python3.5/site-packages/orator/commands`

参考文档：
- orator
    - https://orator-orm.com/docs/0.9/
- laravel database & eloquent
    - https://laravel-china.org/docs/laravel/5.6/database
    - https://laravel-china.org/docs/laravel/5.6/queries
    - https://laravel-china.org/docs/laravel/5.6/migrations
    - https://laravel-china.org/docs/laravel/5.6/seeding
    - https://laravel-china.org/docs/laravel/5.6/eloquent


### `backpack`

这是一个仿 php laravel 框架 [Collection](https://github.com/illuminate/support/blob/master/Collection.php) 的包，能够让我们便捷的操作 python 的 `tuple`, `list`, `map` (不支持 `dict`)。

可以参考这些文档：

- https://github.com/sdispater/backpack
- https://laravel-china.org/docs/laravel/5.6/collections (laravel)

使用参考：

```python
from backpack import collect

d = [dict(x=1, y=2), dict(x=3, y=4)]

print(collect(d).all()) # [{'y': 2, 'x': 1}, {'y': 4, 'x': 3}]
print(collect(d).first()) # {'y': 2, 'x': 1}
print(collect(d).where('x', 1).all()) # [{'y': 2, 'x': 1}]
print(collect(d).pluck('x').all()) # [1, 3]
```

### `pymitter`

这个包提供了事件管理与分发，并通过 decorator 修饰符来定义事件的行为。参考文档：https://github.com/riga/pymitter

使用参考：

```python
from pymitter import EventEmitter

ee = EventEmitter(wildcards=True)

@ee.on("myevent.foo")
def handler1():
    print("handler1 called")

@ee.on("myevent.bar")
def handler2():
    print("handler2 called")

@ee.on("myevent.*") # 可使用通配符来定义事件触发
def hander3():
    print("handler3 called")


ee.emit("myevent.foo")
# -> "handler1 called"
# -> "handler3 called"

ee.emit("myevent.bar")
# -> "handler2 called"
# -> "handler3 called"

ee.emit("myevent.*")
# -> "handler1 called"
# -> "handler2 called"
# -> "handler3 called"
```

## 三、项目结构说明

    .
    ├── app (项目目录)
    │   ├── commands (commands 命令目录)
    │   ├── helpers (项目支持函数目录)
    │   │   ├── application.py (项目相关)
    │   │   ├── common.py (通用函数)
    │   │   ├── constants.py (常量定义)
    │   │   ├── database.py (数据库相关)
    │   │   ├── datetime.py (日期时间相关函数)
    │   │   ├── dictionary.py (dict 辅助函数)
    │   │   └── valid.py (验证函数)
    │   ├── logics (业务逻辑代码目录)
    │   ├── providers (服务提供者目录)
    │   ├── tasks (celery 任务代码目录)
    │   ├── tests (单元测试代码目录)
    │   ├── command.py (command入口)
    │   ├── unittests.py (单元测试入口)
    │   └── utils (工具库)
    ├── bin (项目管理脚本目录)
    │   ├── celery.beat.sh (celery beat 调度器管理脚本)
    │   ├── celery.flower.sh (celery web 控制台管理脚本)
    │   ├── celery.profile.sh (celery 项目环境配置)
    │   ├── celery.run.sh (celery 通用命令运行脚本)
    │   ├── celery.sh (beat/worker 共用管理脚本)
    │   └── celery.worker.sh (celery worker 管理脚本)
    ├── config (配置文件存放目录)
    │   ├── database.yaml
    │   ├── *.yaml
    │   └── testing (测试环境目录)
    │   │   └── database.yaml
    │   └── production
    │       └── database.yaml
    ├── docs (项目文档目录）
    ├── logs (日志目录，按日期存放）
    ├── .python-version (pyenv 环境识别文件)
    ├── requirements_dev.txt (开发环境包依赖文件)
    └── requirements.txt (生产环境包依赖文件)

### typing_environs 
- name = "typing_environs"
- description = "typing_environs add type hints support  for environs"
- authors = ["Euraxluo <euraxluo@qq.com>"]
- license = "The MIT LICENSE"
- repository = "https://github.com/Euraxluo/typing_environs"
_ version = "0.2.*"

#### install
`pip install typing-environs`

#### UseAge
```
from typing_environs import EnvModule, Types


class FLS(EnvModule):
    open: Types.bool
    level: Types.upper
    dir: Types.dir
    rotation: Types.str
    retention: Types.str
    compression: Types.str
    encoding: Types.str
    enqueue: Types.bool
    backtrace: Types.bool
    diagnose: Types.bool


class Log(EnvModule):
    format: Types.str
    dir: Types.dir
    level: Types.upper
    fls: FLS


class Config(EnvModule):  # 默认配置
    env: Types.str
    application: Types.str
    version: Types.str
    data_separator: Types.str

    log: Log

    def __init__(self, *args, paths=["default.env"], **kwargs):
        super(Config, self).__init__(*args, paths=paths, **kwargs)
```

## todo list
- [ ] strict mode
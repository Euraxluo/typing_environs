# -*- coding: utf-8 -*- 
# Time: 2021-08-30 14:03
# Copyright (c) 2021
# author: Euraxluo
import typing_environs.environment
from typing_environs import EnvModule, Types


class FLS(EnvModule):
    open: Types.bool
    level: Types.bool = "sasa"
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


# @EnvModule.export()
class Config(EnvModule):  # 默认配置
    env: Types.str = 1
    application: Types.str
    version: Types.str
    data_separator: Types.str

    log: Log

    def __init__(self, *args, paths=["default.env"], **kwargs):
        super(Config, self).__init__(*args, paths=paths, **kwargs)


def ConfigFactory(separator, strict, **kwargs) -> Config:
    env_paths_mapping = {
        'dev': ["dev.env", "default.env"],
        'fat': ["fat.env", "default.env"],
        'prod': ["prod.env", "default.env"],
        'default': ["default.env"]
    }
    import os
    env = os.environ.get('ENV', default='default').lower()
    config = Config(separator=separator, strict=strict, paths=env_paths_mapping[env])  # 实例化对应的环境
    return config

# -*- coding: utf-8 -*- 
# Time: 2021-08-30 14:03
# Copyright (c) 2021
# author: Euraxluo

import os
from inspect import *
from environs import Env
from easydict import EasyDict
from pydantic import BaseSettings
import typing
import warnings


class Types(object):
    int: Env.int = typing.TypeVar('int')
    bool: Env.bool = typing.TypeVar('bool')
    str: Env.str = typing.TypeVar('str')
    float: Env.float = typing.TypeVar('float')
    decimal: Env.decimal = typing.TypeVar('decimal')
    list: Env.list = typing.TypeVar('list')
    dict: Env.dict = typing.TypeVar('dict')
    json: Env.json = typing.TypeVar('json')
    datetime: Env.datetime = typing.TypeVar('datetime')
    date: Env.date = typing.TypeVar('date')
    time: Env.time = typing.TypeVar('time')
    path: Env.path = typing.TypeVar('path')
    log_level: Env.log_level = typing.TypeVar('log_level')
    timedelta: Env.timedelta = typing.TypeVar('timedelta')
    uuid: Env.uuid = typing.TypeVar('uuid')
    url: Env.url = typing.TypeVar('url')
    enum: Env.enum = typing.TypeVar('enum')
    dj_db_url: Env.dj_db_url = typing.TypeVar('dj_db_url')
    dj_email_url: Env.dj_email_url = typing.TypeVar('dj_email_url')
    dj_cache_url: Env.dj_cache_url = typing.TypeVar('dj_cache_url')

    @staticmethod
    def dir(env, name):
        value = Env.str(env, name)
        if value:
            return os.path.join(os.path.dirname(stack()[2][1]), )
        else:
            return value

    @staticmethod
    def lower(env, name):
        return Env.str(env, name).lower()

    @staticmethod
    def upper(env, name):
        return Env.str(env, name).upper()


class MataBaseSetting(BaseSettings.__class__):
    def __init__(self, *args, **kwargs):
        super(MataBaseSetting, self).__init__(*args, **kwargs)
        if self.__name__ != 'EnvModule' and not hasattr(self, '__instance'):
            self.__instance = "__pre_call__"

    def __call__(self, *args, **kwargs):
        if self.__instance is None or self.__instance == "__pre_call__":
            self.__instance = super(MataBaseSetting, self).__call__(*args, **kwargs)
        return self.__instance

    def __new__(cls, name, bases, attrs):
        init_model = cls.init_models(cls, name, bases, attrs)
        real_cls = type.__new__(cls, name, bases, attrs)
        if init_model:
            EnvModule._MODEL_CLASSES[name.lower()] = real_cls
        return real_cls

    def init_models(cls, name, bases, attrs):
        if '__annotations__' in attrs:
            for k, v in attrs['__annotations__'].items():
                if k in attrs:
                    continue
                elif isclass(v) or isfunction(v):
                    attrs[k] = v
                elif type(v) == typing.TypeVar and v.__name__ in Types.__annotations__:
                    attrs[k] = Types.__annotations__.get(v.__name__)
            return True
        return False

    def __setattr__(self, key, value):
        return super().__setattr__(key, value)

    @property
    def __envs__(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


class EnvModule(BaseSettings, metaclass=MataBaseSetting):
    """
    EnvModule在进行初始化时,能够进行配置文件读取,并且将配置文件注入到类属性中
    继承它,你就能获得该能力,该类的子类被实例化时,会进行配置文件读取和值的装载

    Param: paths,separator,override,strict
    """
    _MODEL_CLASSES = {}
    __envs__ = None

    def _build_values(
            self,
            init_kwargs,
            _env_file=None,
            _env_file_encoding=None,
            _env_nested_delimiter=None,
            _secrets_dir=None
    ):
        paths = init_kwargs.get('paths', [])
        separator = init_kwargs.get('separator', '_')
        override = init_kwargs.get('override', False)
        strict = init_kwargs.get('strict', False)
        env = Env()
        # 从配置的路径列表中读取配置
        for path in paths:
            env.read_env(path=os.path.join(os.path.dirname(getfile(self.__class__)), path), override=override)
        # 注释列表中获取属性,因此强制要求对象类型注解
        all_items = []
        for c in [i for i in self.__class__.mro() if i.__module__ == self.__module__ and '__annotations__' in i.__dict__]:
            for k, v in c.__annotations__.items():
                if hasattr(self, k):
                    all_items.append(k)
                    continue
        # 获取所有的get函数,包括父类
        parse_cache = set()
        for ik in all_items:
            all_envs = dict([(k, v) for k, v in os.environ.items() if k.startswith(ik.upper() + separator) or k == ik.upper() and k not in parse_cache])
            for ek, ev in all_envs.items():
                try:
                    obj, attr, attr_name = self.get_named_attr(EnvModule._MODEL_CLASSES, ek, separator, strict)
                    if attr.__class__ == EasyDict and attr == {}:
                        attr = Env.str
                    setattr(obj, attr_name, attr(env, ek))
                    parse_cache.add(ek)
                except ValueError as e:
                    warnings.warn(f"Parse Warning: {e} ;locals: {env}, {ek}, {ev}, {ik}")
                except Exception as e:
                    raise Exception(f"Parse Error: {e} ;locals: {env}, {ek}, {ev}, {ik}")
        if len(parse_cache) == 0 and strict:
            raise Exception(f"Parse Warning,plz check your env, file:{[os.path.join(os.path.dirname(getfile(self.__class__)), path) for path in paths]},model:{self.__class__}")
        return self

    def get_named_attr(self, templates, obj_name, separator, strict) -> (object, object, str):
        """
        通过对象名和分隔符,从self中进行对象查找,将找到的对象和属性返回
        :param templates:
        :param obj_name:
        :param separator:
        :return:
        """
        # 构造对象
        name_seq = [i.lower() for i in obj_name.split(separator)]
        mount_obj = self.__class__
        obj = None
        for i, name in enumerate(name_seq):
            if not hasattr(mount_obj, name) and not hasattr(mount_obj, separator.join(name_seq[i:])):
                if name in templates or not strict or isinstance(mount_obj, EasyDict):
                    setattr(mount_obj, name, EasyDict())
                elif strict:
                    raise ValueError(f"unknown how to parse env:{obj_name},plz check user model:{self.__class__}")
            elif (not hasattr(mount_obj, name) or isinstance(getattr(mount_obj, name), EasyDict)) and hasattr(mount_obj, separator.join(name_seq[i:])):
                obj = mount_obj
                mount_obj = getattr(mount_obj, separator.join(name_seq[i:]))
                return obj, mount_obj, separator.join(name_seq[i:])

            obj = mount_obj
            mount_obj = getattr(mount_obj, name)
        return obj, mount_obj, name_seq[-1]

# -*- coding: utf-8 -*- 
# Time: 2021-08-30 14:03
# Copyright (c) 2021
# author: Euraxluo

import os
import copy
import typing
import warnings
from inspect import *
from environs import Env
from easydict import EasyDict
from pydantic import BaseSettings


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
            return os.path.abspath(value)
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
    EnvModule?????????????????????,??????????????????????????????,??????????????????????????????????????????
    ?????????,????????????????????????,??????????????????????????????,??????????????????????????????????????????
    TIPS: ????????????????????????
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
        # ???????????????????????????????????????
        for path in paths:
            if isinstance(path, dict):
                for k, v in path.items():
                    if k in os.environ and not override:
                        continue
                    if isinstance(v, str):
                        os.environ[k] = v
                continue
            env.read_env(path=os.path.join(os.path.dirname(getfile(self.__class__)), path), override=override)
        # ???????????????????????????,????????????????????????????????????
        all_items = []
        for c in [i for i in self.__class__.mro() if
                  i.__module__ == self.__module__ and '__annotations__' in i.__dict__]:
            for k, v in c.__annotations__.items():
                if hasattr(self, k):
                    all_items.append(k)
                    continue
        # ???????????????get??????,????????????
        parse_cache = set()
        for ik in all_items:
            all_envs = dict([(k, v) for k, v in os.environ.items() if
                             k.startswith(ik.upper() + separator) or k == ik.upper() and k not in parse_cache])
            for ek, ev in all_envs.items():
                try:
                    obj, attr, attr_name = self.get_named_attr(EnvModule._MODEL_CLASSES, ek, separator, strict)
                    if attr.__class__ == EasyDict and attr == {}:
                        attr = Env.str
                    setattr(obj, attr_name, attr(env, ek))
                    parse_cache.add(ek)
                except ValueError as e:
                    warnings.warn(f"Parse Warning: {e} ;locals:{ek}, {ev}, {ik}")
                except Exception as e:
                    warnings.warn(f"Parse Error: {e} ;locals:{ek}, {ev}, {ik}")
        if len(parse_cache) == 0 and strict:
            raise Exception(
                f"Parse Warning,plz check your env, file:{[os.path.join(os.path.dirname(getfile(self.__class__)), path) for path in paths if isinstance(path, str)]},model:{self.__class__}")
        return self

    def search(self, node, name_seq, height, separator, node_name=None):
        if len(name_seq) == height:
            return None, node, node_name
        x = []
        for o in [n for n in ['_'.join(j) for j in [copy.deepcopy(x) for i in name_seq[height:] if not x.append(i)]] if
                  hasattr(node, n)]:
            last, result, node_name = self.search(getattr(node, o), name_seq, height + len(set(o.split(separator))),
                                                  separator, o)
            if result is not None:
                if last is None:
                    last = node
                return last, result, node_name
        return None, None, node_name

    def get_named_attr(self, templates, obj_name, separator, strict) -> (object, object, str):
        """
        ???????????????????????????,???self?????????????????????,?????????????????????????????????
        :param templates:
        :param obj_name:
        :param separator:
        :return:
        """
        # ????????????
        name_seq = [i.lower() for i in obj_name.split(separator)]
        mount_obj = self.__class__
        obj, attr, attr_name = self.search(mount_obj, name_seq, 0, separator)
        return obj, attr, attr_name

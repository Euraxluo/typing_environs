# -*- coding: utf-8 -*- 
# Time: 2021-10-20 10:07
# Copyright (c) 2021
# author: Euraxluo
from .envs.models import *

def config_factory():
    config: Config = ConfigFactory(separator='.', strict=True)
    return config


__all__ = ["Config"]

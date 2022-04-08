# -*- coding: utf-8 -*- 
# Time: 2021-10-20 16:35
# Copyright (c) 2021
# author: Euraxluo

from unittest import TestCase
from .envs2.models import Config as Config2

from .envs.models import *


class Test(TestCase):
    def get_config_class(self, config):
        d = config
        print(d.env)
        print(d.application)
        print(d.version)
        print(d.data_separator)
        print("================= log env=================")
        print(d.log)
        print(d.log.dir)
        print(d.log.level)
        print(d.log.format)
        print("================= fls env=================")
        print(d.log.fls)
        print(d.log.fls.open)
        print(d.log.fls.level)
        print(d.log.fls.dir)
        print(d.log.fls.rotation)
        print(d.log.fls.retention)
        print(d.log.fls.compression)
        print(d.log.fls.encoding)
        print(d.log.fls.enqueue)
        print(d.log.fls.backtrace)
        print(d.log.fls.diagnose)
        print(d.log.fls.__envs__)

    def test_default_config2(self):
        x = Config2(strict=True, separator='_', paths=["default.env"])
        self.get_config_class(x)

    def test_default_config(self):
        x = Config(strict=True, separator='.', paths=["default.env"])
        self.get_config_class(x)

    def test_dev_config(self):
        x = Config(strict=True, separator='.', paths=["dev.env", "default.env"])
        self.get_config_class(x)

    def test_fat_config(self):
        x = Config(strict=True, separator='.', paths=[{"ENV": "sasadsad"}, "fat.env", "default.env"])
        self.get_config_class(x)

    def test_prod_config(self):
        x = Config(strict=True, separator='.', paths=["prod.env", "default.env"])
        self.get_config_class(x)

    def test_config_factory(self):
        import os
        os.environ['ENV'] = 'prod'
        x = ConfigFactory(separator='.', strict=True)
        self.get_config_class(x)

    def test_config_factory(self):
        import os
        os.environ['ENV'] = 'dev'
        x = ConfigFactory(separator='.', strict=True)
        self.get_config_class(x)

    def test_config_factory(self):
        import os
        os.environ['ENV'] = 'fat'
        x = ConfigFactory(separator='.', strict=True)
        self.get_config_class(x)

    def test_config_factory(self):
        import os
        os.environ['ENV'] = 'default'
        x = ConfigFactory(separator='.', strict=True)
        self.get_config_class(x)

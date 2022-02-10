### 环境配置

default.env 为默认配置

dev.env 为本机开发配置

fat.env 为线上环境配置

prod.env 为正式环境配置

#### 添加配置
当你需要修改/添加配置时
1. 确定该配置在 default中是否存在
    1. 如果存在,那么针对你想添加/修改的环境,在对应的{dev,fat,prod}中添加/修改配置
    2. 不存在,那么首先需要在default中添加该配置,并且在environment中添加class(BaseModel)或者是在已有的类中进行添加
2. 类的含义
```python
class App(BaseSetting):
    name: ParseTyping.str
    host: ParseTyping.str
    port: ParseTyping.int
    debug: ParseTyping.bool
    reload: ParseTyping.bool

    cors_origins: ParseTyping.list
    project_name: ParseTyping.str
    project_description: ParseTyping.str
    api_prefix: ParseTyping.str
    log_level: ParseTyping.lower
```    
`BaseSetting`继承了pydantic中BaseSettings,能够提供自动补全和类型定义,通过元类MataBaseSetting的处理,我们能够将类型标识environs.Env
所有字段的类型都是基础类型,标识,将来获取到该配置时的真实类型.
# Data Center Service Automation Development Project

dcs 自动化测试项目主要负责测试重构后的DCS项目在PFS产品的应用场景。项目采用Python 语言进行开发，主要使用了开源的pytest、pytest-mock等主流微服务测试和API接口依赖框架进行自动化测试开发。

# Installation

安装项目依赖的三方Python library：

`pip install pytest-mock`

`pip install hoverpy`

`pip install redis`

`pip install hiredis`

`pip install allure-pytest`

`pip install pytest`

`pip install pytest-check`


#   Usage

pytest -sv --alluredir "%allure_result_directory%" "--clean-alluredir"


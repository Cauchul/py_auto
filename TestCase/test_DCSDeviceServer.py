# -*- coding:utf-8 -*-
import allure
import pytest

from Common.GobalVariabies import *


@allure.feature("设备服务测试用例")
class TestDCSDeviceServer:

    def setup_class(self): # 这是在所有用例运行之前运行
        with allure.step('这里是 setup_class'):
            print('这里是 setup_class')
    def teardown_class(self): # 这是在所有用例结束之后运行
        with allure.step('这里是 teardown_class'):
            print('这里是 teardown_class')

    @pytest.mark.skip(reason="跳过设备服务")
    @allure.step('判断设备状态')
    def test_dcs_device_server(self):
        with allure.step('这里是 setup_class'):
            print('这里是 setup_class')
        print('用例开始')
        device_id = get_device_id_from_redis()
        port_list = get_can_use_module_port(device_id)
        with allure.step('所有的测试端口为：{0}'.format(port_list)):
            print('port_list: ', port_list)
        for port in port_list:
            with allure.step('当前测试端口：{0}'.format(port)):
                redis_hash_name = device_id + '-DCSDeviceServer-{0}'.format(port)
                with allure.step('redis hash name为：{0}'.format(redis_hash_name)):
                    module_status = f_redis.hget(redis_hash_name, 'module_status')
                with allure.step('断言，module_status， 期望值：Servering， 实际值：{0}'.format(module_status)):
                    assert module_status == 'Servering'
        print('用例结束')
        with allure.step('这里是 teardown_class'):
            print('这里是 teardown_class')


if __name__ == "__main__":
    pass

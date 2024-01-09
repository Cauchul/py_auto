# -*- coding:utf-8 -*-
import csv
import os
import time

import allure
import pytest

from Common.GobalVariabies import local_tmp_path
from RemoteControl.TA_interface import *
from RemoteControl.conftest import ta_prepare_test


def call_function(func, *arg):
    failed_func_name, res_statues = func(*arg)
    TestTA.func_dict[failed_func_name] = res_statues


@allure.feature("设备服务测试用例")
class TestTA:
    func_dict = {}
    def setup_class(self):
        with allure.step('连接socket'):
            csv_header_list = ['UE index', '命令名称', '响应时间', '发送命令内容', '命令返回值', '命令返回状态']
            TestTA.file = open(os.path.join(local_tmp_path, 'TA_interface_data.csv'), 'w', newline='')
            TestTA.writer = csv.writer(TestTA.file)
            TestTA.writer.writerow(csv_header_list)
            connect_socket()

    def teardown_class(self):
        with allure.step('关闭socket'):
            close_socket_conn()
            TestTA.file.close()

    def demo_test(self):
        print('demo_test_func')

    # @pytest.mark.usefixtures('ta_prepare_test')
    @allure.step('TA单UE测试')
    def test_case_ta_interface(self):
        start_time = time.time()
        with allure.step('扫描设备'):
            time_out = 10
            while True:
                res = auto_check()
                # 超时检测
                if time_out < time.time() - start_time:
                    with check.check:
                        with allure.step(
                                '命令：{0}，状态码，期望值：0，实际值：{1}'.format('AutoCheck', res['Param']['State'])):
                            assert 0 == res['Param']['State']
                    with allure.step('auto_check 超时退出'):
                        assert time.time() - start_time < time_out
                if 0 == res['Param']['State']:
                    end_time = time.time()
                    with check.check:
                        with allure.step(
                                '命令：{0}，状态码，期望值：0，实际值：{1}'.format('AutoCheck', res['Param']['State'])):
                            assert 0 == res['Param']['State']
                    with allure.step('auto_check 花费时长为:{0}'.format(end_time - start_time)):
                        print('auto_check 花费时长为:{0}'.format(end_time - start_time))
                    TestTA.ue_index_list = res['Param']['WorkingIndex']
                    break
        with allure.step('连接设备'):
            call_function(connect_devices, TestTA.writer)
        with allure.step('开始记录'):
            call_function(start_log, TestTA.writer)
        for idx in TestTA.ue_index_list:
            print('idx: ', idx)
            print('ue_index_list: ', TestTA.ue_index_list)
            with allure.step('发送AT命令'):
                call_function(send_at_command, 'ATI', TestTA.writer, idx)
            with allure.step('设置设置模块5G模式'):
                call_function(config_5G_deployment, TestTA.writer, idx)
            with allure.step('设置模块NSSAI'):
                call_function(setups_NSSAI, TestTA.writer, idx)
            with allure.step('设置模块PDU'):
                call_function(setup_PDU, TestTA.writer, idx)
            with allure.step('设置模块APN'):
                call_function(configure_APN, TestTA.writer, idx)
            with allure.step('打入start statist tag'):
                call_function(start_statist_ics, TestTA.writer, idx)
            with allure.step('模块软下电'):
                call_function(power_off, TestTA.writer, idx)
            with allure.step('模块软上电'):
                call_function(power_on, TestTA.writer, idx)
            # with allure.step('开始iperf业务'):
            #     failure_func_list.append(start_traffic())
            # with allure.step('执行ftp download业务'):
            #     start_ftp_dl()
            # with allure.step('执行联合任务'):
            #     start_composite_test_plan()
            # with allure.step('执行ping业务'):
            #     start_ping()
            # with allure.step('执行iperf上行业务'):
            #     start_ul_traffic()
            # with allure.step('开始call业务'):
            #     start_call()
            # with allure.step('开始mos业务'):
            #     start_mos()
            # with allure.step('执行ftp上行业务'):
            #     start_ftp_ul()
            # with allure.step('停止测试'):
            #     call_function(stop_test_plan)
            with allure.step('获取数据链路层上下行数据量'):
                call_function(get_param_mac, TestTA.writer, idx)
            with allure.step('获取模块IMSI'):
                call_function(get_param_imsi, TestTA.writer, idx)
            with allure.step('获取模块IMEI'):
                call_function(get_param_imei, TestTA.writer, idx)
            with allure.step('获取模块ip'):
                call_function(get_param_ip, TestTA.writer, idx)
            with allure.step('获取PDU信息'):
                call_function(get_pdu_info, TestTA.writer, idx)
            with allure.step('获取模块网络状态'):
                call_function(get_attach_status, TestTA.writer, idx)
            with allure.step('打入stop statist tag'):
                call_function(stop_statist_ics, TestTA.writer, idx)
            with allure.step('获取statist tag中的结果'):
                call_function(get_statistics_result, TestTA.writer, idx)
            with allure.step('获取statist tag中的参数结果'):
                call_function(get_param_statistics_result, TestTA.writer, idx)
            with allure.step('获取statist tag中的事件结果'):
                call_function(get_event_statistics_result, TestTA.writer, idx)
            with allure.step('获取statist tag中的参数摘要结果'):
                call_function(get_param_summary_statistics_result, TestTA.writer, idx)
            # loop_settings()
        with allure.step('停止记录'):
            call_function(stop_log, TestTA.writer)
        TestTA.func_dict = {k: v for k, v in TestTA.func_dict.items() if v != 0}
        print('TestTA.func_dict: ', TestTA.func_dict)
        with allure.step('失败的接口'):
            for func_name in TestTA.func_dict:
                with allure.step('失败接口名称：{0}，接口返回状态值：{1}'.format(func_name, TestTA.func_dict[func_name])):
                    pass


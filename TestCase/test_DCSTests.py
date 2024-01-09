# -*- coding:utf-8 -*-
from datetime import datetime
import json
import os
import subprocess
import threading
import time

import allure
import pytest
import sys

from pytest_check import check

# from Common.Operation import *
from Common.GobalVariabies import *

sys.path.append("..")


def update_test_plan(test_plan_id):
    get_test_plan_cmd = 'select "test_plan_data"."test_plan_xml" from ' \
                        '"public"."test_plan_data" WHERE ' \
                        '"test_plan_data"."id" = {0}'.format(test_plan_id)
    print('get_test_plan_cmd: ', get_test_plan_cmd)
    serial_test_plan_data = pg_project.pg_run_sql_fetchall(get_test_plan_cmd)

    pg_insert_cmd = 'INSERT INTO "public"."testplan_history" (unified_xml, dev_id) VALUES (\'{0}\', \'{1}\')'.format(
        serial_test_plan_data[0][0], TestDCSTests.device_id)
    pg_project.pg_insert_data(pg_insert_cmd)


def send_start_work_cmd(port, ui_project):
    update_cmd = {"API": "StartWork", "Params": {'TestPort': int(port), 'RequestId': ''}}
    with allure.step('发送的命令为：{0}'.format(update_cmd)):
        ui_project.send(json.dumps(update_cmd))


def send_stop_work_cmd(port, ui_project):
    stop_work_cmd = {"API": "StopWork", "Params": {'TestPort': int(port), 'RequestId': ''}}
    with allure.step('发送的命令为：{0}'.format(stop_work_cmd)):
        ui_project.send(json.dumps(stop_work_cmd))


def send_updatetestplan_cmd(update_port):
    update_cmd = {"API": "UpdateTestplan",
                  "Params": {"Name": "", "TimeZone": "", "TestPlanXml": "", "Origin": 0, "TestPort": int(update_port),
                             "RequestId": "", "IsTest": True}}
    with allure.step('发送的命令为：{0}'.format(update_cmd)):
        ui_service_project.send(json.dumps(update_cmd))


def send_start_test_plan_cmd(update_port, ui_project):
    start_test_cmd = {"API": "StartTestPlan",
                      "Params": {"FileName": "", "IsFileCut": 0, "TestPort": int(update_port), "RequestId": ""}}
    with allure.step('发送的命令为：{0}'.format(start_test_cmd)):
        ui_project.send(json.dumps(start_test_cmd))


def deal_get_qos_task_total_run_count(test_schedule_data):
    total_group_count = test_schedule_data['total_group_count']
    total_parallel_group_count = test_schedule_data['total_parallel_group_count']
    return int(total_group_count) * int(total_parallel_group_count)


def check_qos_xml_data(xml_deal_data, qos_deal_data):
    with check.check:
        for x_key in xml_deal_data:
            with allure.step('对比业务 {0} 的测试次数， 期望值：{1}，实际值：{2}'.format(x_key, xml_deal_data[x_key],
                                                                                     qos_deal_data[x_key])):
                assert xml_deal_data[x_key] == qos_deal_data[x_key]


def deal_test_plan_get_data(xml_data):
    res_data = {}
    total_count_dict = {}
    group_name = xml_data[0]['GroupName']
    for data in xml_data:
        if group_name != data['GroupName']:
            group_name = data['GroupName']
        if 'total_parallel_group_count' in data.keys():
            total_count = int(data['total_group_count']) * int(data['total_parallel_group_count'])
            if data['TaskType'] in res_data.keys():
                task_count = int(data['TaskRepeatCount']) * total_count + res_data[data['TaskType']]
            else:
                task_count = int(data['TaskRepeatCount']) * total_count
        else:
            total_count = int(data['total_group_count'])
            if data['TaskType'] in res_data.keys():
                task_count = int(data['TaskRepeatCount']) * total_count + res_data[data['TaskType']]
            else:
                task_count = int(data['TaskRepeatCount']) * total_count
        res_data[data['TaskType']] = task_count
        total_count_dict[group_name] = total_count
    return res_data, total_count_dict


def generate_port_test_plan_xml(port):
    # 将pg中的端口测试计划，生成xml文件
    sql_cmd_testplan_config_port_def = 'select "testplan_config_port_def"."testschemas" from ' \
                                       '"public"."testplan_config_port_def" WHERE ' \
                                       '"testplan_config_port_def"."port" = {0}'.format(port)
    # 根据端口构建xml文件名称
    port_xml_name_testplan_config_port_def = os.path.join(local_tmp_path,
                                                          'testplan_config_port_{0}_def_pg_data.xml'.format(
                                                              port))
    pg_project.pg_run_sql_generate_xml(sql_cmd_testplan_config_port_def,
                                       port_xml_name_testplan_config_port_def, 'testschemas')


def send_start_cmd(port, ui_service_project):
    with allure.step('更新测试计划'):
        print('更新测试计划')
        update_cmd = {"API": "UpdateTestplan",
                      "Params": {"Name": "", "TimeZone": "", "TestPlanXml": "", "Origin": 0, "TestPort": int(port),
                                 "RequestId": "", "IsTest": True}}
        with allure.step('发送update_testplan命令: {0}'.format(update_cmd)):
            print('发送update_testplan命令 {0}'.format(update_cmd))
            ui_service_project.send(json.dumps(update_cmd))
    # 发送 start_work 命令
    send_start_work_cmd(port, ui_service_project)
    time.sleep(10)
    task_start_test_time = datetime.today()
    with allure.step('开始测试'):
        print('开始测试')
        start_cmd = {"API": "StartTestPlan",
                     "Params": {"FileName": "", "IsFileCut": 0, "TestPort": int(port), "RequestId": ""}}
        with allure.step('发送start_test命令: {0}'.format(start_cmd)):
            print('发送start_test命令 {0}'.format(start_cmd))
            ui_service_project.send(json.dumps(start_cmd))
    time.sleep(5)
    return task_start_test_time


def set_data_set_hash_key_pull_port(hash_name, set_key, set_value):
    f_redis.hset(hash_name, set_key, set_value)


def wait_test_complete(hash_key):
    # 等待测试完成
    cr_count = 0
    while True:
        test_status = f_redis.hget(hash_key, 'test_status')
        print('test_status: ', test_status)
        if 'Idle' == test_status:
            time.sleep(5)
            with allure.step('业务结束'):
                print('业务结束')
                break
        else:
            cr_count += 1
            with allure.step('第{0}次检测，业务还在进行中，等待五秒后再次检查'.format(cr_count)):
                print('第{0}次检测，业务还在进行中，等待五秒后再次检查'.format(cr_count))
            time.sleep(5)

        # if 'Preparing' == test_status or 'Testing' == test_status:
        #     cr_count += 1
        #     with allure.step('第{0}次检测，业务还在进行中，等待五秒后再次检查'.format(cr_count)):
        #         print('第{0}次检测，业务还在进行中，等待五秒后再次检查'.format(cr_count))
        #     time.sleep(5)
        # else:
        #     with allure.step('业务结束'):
        #         print('业务结束')
        #         break


def get_test_plan_xml_data(port):
    res_list = []
    xml_name = os.path.join(local_tmp_path, 'testplan_config_port_{0}_def_pg_data.xml'.format(port))
    if not os.path.exists(xml_name):
        with check.check:
            with allure.step('Failed, 端口 {0} 的测试计划xml文件 {1} 未找到'.format(port, xml_name)):
                assert os.path.exists(xml_name)
                return
    root = ParseXml.get_root_by_xml_name(xml_name)
    task_groups_node = ParseXml.get_root_by_element_name(root, 'TaskGroups')

    for group_config in task_groups_node:
        normal_tmp_dict = {}
        parallel_tmp_dict = {}
        group_config_data = ParseXml.parse_xml_data_to_dict_by_node(group_config)
        print('group_config_data: ', group_config_data)
        tasks_node = ParseXml.get_root_by_element_name(group_config, 'Tasks')
        for task_config in tasks_node:
            task_config_data = ParseXml.parse_xml_data_to_dict_by_node(task_config)
            print('task_config_data: ', task_config_data)

            if 'Parallel Service' != task_config_data['TaskType']:
                normal_tmp_dict['GroupName'] = group_config_data['GroupName']
                normal_tmp_dict['total_group_count'] = group_config_data['GroupRepeatCount']
                normal_tmp_dict['TaskType'] = task_config_data['TaskType']
                normal_tmp_dict['TaskRepeatCount'] = task_config_data['TaskRepeatCount']
                res_list.append(normal_tmp_dict)
                normal_tmp_dict = {}

            for node in task_config:
                if 'TaskType' == node.tag and 'Parallel Service' == node.text:  # 并行
                    task_list_node = ParseXml.get_root_by_element_name(task_config, 'TaskList')
                    for task in task_list_node:
                        task_data = ParseXml.parse_xml_data_to_dict_by_node(task)
                        print('task_data: ', task_data)
                        parallel_tmp_dict['GroupName'] = group_config_data['GroupName']
                        parallel_tmp_dict['total_group_count'] = group_config_data['GroupRepeatCount']
                        parallel_tmp_dict['parallel_group_TaskType'] = task_config_data['TaskType']
                        parallel_tmp_dict['total_parallel_group_count'] = task_config_data['TaskRepeatCount']
                        parallel_tmp_dict['TaskType'] = task_data['TaskType']
                        parallel_tmp_dict['TaskRepeatCount'] = task_data['TaskRepeatCount']
                        res_list.append(parallel_tmp_dict)
                        parallel_tmp_dict = {}
    print('--' * 50)
    print(res_list)
    print('--' * 50)
    return res_list


def parse_xml_parallel_task_data(root, task_list):
    part_str = {}
    total_count = 0
    for neighbor in root.iter():
        if 'GroupRepeatCount' == neighbor.tag:
            total_count = int(neighbor.text)
        if 'Tasks' == neighbor.tag:
            print(neighbor)
            for node in neighbor[0]:
                if 'TaskRepeatCount' == node.tag:
                    total_count = int(node.text) * total_count
        if 'TaskList' == neighbor.tag:
            print(neighbor)
            for node in neighbor:
                for i in node:
                    part_str[i.tag] = str(i.text)
                for i in part_str:
                    part_str[i] = part_str[i].strip()
                task_list.append(part_str)
                part_str = {}
    return total_count


def parse_xml_normal_task_data(root, task_list):
    part_str = {}
    total_count = 0
    for neighbor in root.iter():
        if 'GroupRepeatCount' == neighbor.tag:
            total_count = int(neighbor.text)
        if 'Tasks' == neighbor.tag:
            print(neighbor)
            for node in neighbor[0]:
                part_str[node.tag] = str(node.text)
                for i in part_str:
                    part_str[i] = part_str[i].strip()
    task_list.append(part_str)
    return total_count


def get_event_count_from_pg(port, task_start_test_time, event_code):
    # 根据对应端口，读取pg中的数据
    sql_cmd = 'select COUNT("device_event_def"."event_code") from "public"."device_event_def" WHERE ' \
              '"device_event_def"."port" = {0} AND "device_event_def"."event_datetime" > \'{1}\' ' \
              'AND "device_event_def"."event_code" = {2}'.format(port, task_start_test_time, event_code)
    pg_event_count = pg_project.pg_run_sql_fetchall(sql_cmd)
    print('pg_event_count: ', pg_event_count)
    return pg_event_count


def get_event_data_from_pg(port, task_start_test_time, event_code):
    # 根据对应端口，读取pg中的数据
    res_data = []
    sql_cmd = 'select "device_event_def"."event_code" from "public"."device_event_def" WHERE ' \
              '"device_event_def"."port" = {0} AND "device_event_def"."event_datetime" > \'{1}\' ' \
              'AND "device_event_def"."event_code" = {2}'.format(port, task_start_test_time, event_code)
    print('sql_cmd: ', sql_cmd)
    pg_event_code_data = pg_project.pg_run_sql_fetchall(sql_cmd)
    for data in pg_event_code_data:
        res_data.append(data[0])
    return res_data


def get_test_schedule_data_from_redis(port, device_id):
    # 获取hash key
    hash_key = device_id + '-DCSTestSchedule-' + str(port)
    return f_redis.hgetall(hash_key)


def check_qos_event_code_data(port, xml_set_times, task_start_test_time):
    print('xml_set_times: ', xml_set_times)
    # with allure.step('postgres 事件code和测试计划业务配置次数，数据对比'.format(port)):
    for q_task in xml_set_times:
        # 获取失败次数
        fail_times = 0
        for fail_code in TestDCSTests.fail_event_code_list[q_task]:
            fail_times += get_event_count_from_pg(port, task_start_test_time, fail_code)[0][0]
            print('失败code：{0}，当前业务：{1}，失败code出现次数：{2}'.format(fail_code, q_task, fail_times))
        for event_code in TestDCSTests.event_code_list[q_task]:
            # code_times = len(get_event_data_from_pg(port, task_start_test_time, event_code))
            code_times = get_event_count_from_pg(port, task_start_test_time, event_code)[0][0]
            print('事件code：{0}，当前业务：{1}，事件code出现次数：{2}，执行总次数：{3}'.format(event_code, q_task, code_times, xml_set_times[q_task]))
            print('--' * 100)
            if xml_set_times[q_task] == code_times:
                with allure.step(
                        'success, 端口{0}事件code：DEC:{1}，HEX:{2}, 期望出现次数：{3},实际出现次数：{4}'.format(
                            port, event_code, hex(event_code), xml_set_times[q_task], code_times)):
                    assert xml_set_times[q_task] == code_times
            elif xml_set_times[q_task] == code_times + fail_times:
                with allure.step(
                        'success, 端口{0}事件code：DEC:{1}，HEX:{2}, 期望出现次数：{3},实际出现次数：{4}'.format(
                            port, event_code, hex(event_code), xml_set_times[q_task], code_times + fail_times)):
                    assert xml_set_times[q_task] == code_times + fail_times
            else:
                with check.check:
                    with allure.step(
                            'Failed, 端口 {0} 的事件code：DEC:{1}，HEX:{2}, 期望出现次数：{3},实际出现次数：{4}'.format(
                                port, event_code, hex(event_code), xml_set_times[q_task], code_times + fail_times)):
                        assert xml_set_times[q_task] == code_times + fail_times


def start_test_and_check_res(port, hash_key, device_id):
    with allure.step('当前测试端口：{0}'.format(port)):
        with allure.step('发送控制命令'):
            with allure.step('通过ui，发送 UpdateTestplan 命令'):
                send_updatetestplan_cmd(port)
            with allure.step('通过ui，发送 StartWork 命令'):
                send_stop_work_cmd(port, ui_service_project)
                # redis_chanel = device_id + '-DCSDataSets-{0}-cmdrequest'.format(port)
                # json_cmd_send_start_work(redis_chanel, port)
                send_start_work_cmd(port, ui_service_project)
            with allure.step('通过ui，发送 StartTestPlan 命令'):
                send_start_test_plan_cmd(port, ui_service_project)
            task_start_test_time = datetime.today()
            with allure.step('业务开始时间为：{0}'.format(task_start_test_time)):
                print('task_start_test_time: ', task_start_test_time)
            time.sleep(5)
        with allure.step('等待测试业务执行完成'.format(hash_key)):
            wait_test_complete(hash_key)
            time.sleep(5)
        with allure.step('通过ui，发送 StopWork 命令'):
            # print('redis_chanel: ', redis_chanel)
            # json_cmd_send_stop_work(redis_chanel, port)
            send_stop_work_cmd(port, ui_service_project)
            time.sleep(3)
        with allure.step('检查业务执行次数'):
            with allure.step('解析端口 {0} 的测试计划'.format(port)):
                generate_port_test_plan_xml(port)
                xml_data = get_test_plan_xml_data(port)
                print('xml_data: ', xml_data)
                xml_deal_data, total_count_dict = deal_test_plan_get_data(xml_data)
                with allure.step('业务数据为：{0}，执行总次数为：{1}'.format(xml_deal_data, total_count_dict)):
                    print('xml_deal_data: ', xml_deal_data)
                    print('total_count: ', total_count_dict)
            with allure.step('解析 redis 中，端口 {0}， redis 中 DCSTestSchedule 的数据'.format(port)):
                test_schedule_data = get_test_schedule_data_from_redis(port, device_id)
                qos_total_count = deal_get_qos_task_total_run_count(test_schedule_data)
                with allure.step('解析出的业务执行总次数为：{0}'.format(qos_total_count)):
                    print('qos_total_count: ', qos_total_count)
            with allure.step('业务执行总次数次数对比， 期望值：{0}，实际值：{1}'.format(list(total_count_dict.values())[-1],
                                                                       qos_total_count)):
                assert list(total_count_dict.values())[-1] == qos_total_count
        with allure.step('检查业务事件'):
            print('检查业务事件')
            check_qos_event_code_data(port, xml_deal_data, task_start_test_time)


def json_cmd_send_start_work(redis_chanel, port):
    data_path = os.path.join(local_tmp_path, 'test_ui_service_{0}'.format(port))
    if os.path.exists(data_path + '.ddib'):
        os.remove(data_path + '.ddib')

    cmd_json_update_testplan = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                                'method': 'start_work',
                                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDcs-10',
                                'test_port': port, 'file_name': data_path}
    cmd_update_testplan_res = pub_json_cmd_to_redis_chanel(TestDCSTests.package_project, cmd_json_update_testplan, pubsub,
                                                           redis_chanel)
    print('cmd_update_testplan_res: ', cmd_update_testplan_res)


def json_cmd_send_stop_work(redis_chanel, port):
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'stop_work',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSTestMgr-10',
                'test_port': port}

    pub_json_cmd_to_redis_chanel(TestDCSTests.package_project, cmd_json, pubsub,
                                 redis_chanel)


@allure.feature('DCSTest业务测试')
class TestDCSTests:
    event_code_list = {
        'Ping': [0x190, 0x192],
        'HTTP Download': [0xAB, 0XA2, 0XA3, 0XA5],
        'FTPDownload': [0x80, 0x82, 0x83, 0x85],
        'HTTP Upload': [0xF0C, 0xF03, 0xF04, 0xF06],
        'IPerf': [0xE02, 0xE03, 0xE08, 0xE09],
        'MOC': [0xA, 0x30170, 0x30171, 0x30172, 0x30173, 0xB],
        'MTC': [0x64, 0x30180, 0x30181, 0x30182, 0x30183],
        'FTP Upload': [0x90, 0x98, 0x9A, 0x92, 0x93, 0x95],
        'FTP Download': [0x80, 0x88, 0x8A, 0x82, 0x83, 0x85]
    }
    fail_event_code_list = {
        'Ping': [0x193],
        'HTTP Download': [],
        'FTPDownload': [0x84],
        'HTTP Upload': [],
        'IPerf': [0xE04, 0xE05],
        'MOC': [],
        'MTC': [],
        'FTP Upload': [0x9C],
        'FTP Download': [0x84]
    }

    def setup_class(self):
        pubsub.subscribe('PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest-cmdrequest')
        TestDCSTests.device_id = get_device_id_from_redis()
        print('device_id: ', TestDCSTests.device_id)

        TestDCSTests.package_project = PackageUnpack(dll_path)
        redis_chanel = TestDCSTests.device_id + '-DCSTestMgr-cmdrequest'
        print('channel: ', redis_chanel)

        with allure.step('获取可以使用的模块端口'):
            dev_hash_name = get_all_run_process(TestDCSTests.device_id)
            TestDCSTests.test_port_list = check_module(dev_hash_name)

            with allure.step('期望值：值不为空，实际值：{0}'.format(TestDCSTests.test_port_list)):
                print('TestDCSTests.test_port_list: ', TestDCSTests.test_port_list)
                # assert TestDCSTests.test_port_list

        with allure.step('连接UIService'):
            websocket_status = ui_service_project.connect()
            with check.check:
                with allure.step('断言 UIService 的连接状态是否为101. {0}'.format(websocket_status == 101)):
                    assert websocket_status == 101

    def teardown_class(self):
        ui_service_project.disconnect()
        pubsub.unsubscribe('PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest-cmdrequest')

    @allure.step('DCSTest并行测试测试')
    def test_dcs_test_parallel_test_plan(self):
        print('开始进行，DCSTest并行测试测试')
        time.sleep(8)
        keys = f_redis.get_redis_keys()
        print('keys: ', keys)
        for hash_key in keys:
            if 'DCSTestSchedule' in hash_key:
                print('hash_key: ', hash_key)
                f_redis.delete(hash_key)
        time.sleep(5)

        update_test_plan(test_plan_id=2)
        thread_list = []
        for port in TestDCSTests.test_port_list:
            hash_key = TestDCSTests.device_id + '-DCSTestSchedule-' + str(port)
            t = threading.Thread(target=start_test_and_check_res, args=(port, hash_key, TestDCSTests.device_id))
            t.start()
            # print(threading.enumerate())
            thread_list.append(t)

        for i in thread_list:
            i.join()

    @allure.step('DCSTest串行测试')
    def test_dcs_test_serial_test_plan(self):
        keys = f_redis.get_redis_keys()
        print('keys: ', keys)
        for hash_key in keys:
            if 'DCSTestSchedule' in hash_key:
                print('hash_key: ', hash_key)
                f_redis.delete(hash_key)
        time.sleep(5)

        update_test_plan(test_plan_id=1)

        thread_list = []
        for port in TestDCSTests.test_port_list:
            hash_key = TestDCSTests.device_id + '-DCSTestSchedule-' + str(port)
            t = threading.Thread(target=start_test_and_check_res, args=(port, hash_key, TestDCSTests.device_id))
            t.start()
            # print(threading.enumerate())
            thread_list.append(t)

        for i in thread_list:
            i.join()

    @allure.step('DCSTest串并联合测试')
    def test_dcs_test_serial_with_parallel_test_plan(self):
        print('开始进行，DCSTest串并联合测试')
        time.sleep(8)
        keys = f_redis.get_redis_keys()
        print('keys: ', keys)
        for hash_key in keys:
            if 'DCSTestSchedule' in hash_key:
                print('hash_key: ', hash_key)
                f_redis.delete(hash_key)
        time.sleep(5)

        update_test_plan(test_plan_id=3)

        thread_list = []
        for port in TestDCSTests.test_port_list:
            hash_key = TestDCSTests.device_id + '-DCSTestSchedule-' + str(port)
            t = threading.Thread(target=start_test_and_check_res, args=(port, hash_key, TestDCSTests.device_id))
            t.start()
            # print(threading.enumerate())
            thread_list.append(t)

        for i in thread_list:
            i.join()


if __name__ == "__main__":
    pass

import subprocess
import threading

from pytest_check import check

from Common.DataFactory import *
from random import choice
from Common.GobalVariabies import *

import time
import json
import allure
import websocket
import asyncio


def send_ui_service_cmd_get_res(ui_service_cmd):
    return ui_service_project.send_get_res(json.dumps(ui_service_cmd))


def check_ui_service_cmd_res(res_data, hash_data, port):
    change_dict = {'IPv4Address': 'module_netadopt_ipv4', 'IMEI': 'module_imei', 'ATPort': 'module_at_port',
                   'TracePort': 'module_diag_port', 'NetadoptName': 'module_netadopt_name',
                   'ModuelChipvendor': 'module_chipvendor'}
    if res_data['Data']:
        for data in res_data['Data']:
            print('data[TestPort]: ', data['TestPort'])
            if int(port) == int(data['TestPort']):
                print('data: ', data)
                for d_key in change_dict:
                    with allure.step(
                            '对比 {0} 数据， 期望值：{1}， 实际值：{2}'.format(d_key, hash_data[change_dict[d_key]],
                                                                           data[d_key])):
                        if '' == hash_data[change_dict[d_key]]:
                            hash_data[change_dict[d_key]] = None
                        assert hash_data[change_dict[d_key]] == data[d_key]
    else:
        for d_key in change_dict:
            with allure.step(
                    '对比 {0} 数据， redis中的值：{1}， 命令返回值：{2}'.format(d_key, hash_data[change_dict[d_key]], '')):
                assert hash_data[change_dict[d_key]] == ''


def send_cmd(cmd):
    print('cmd: ', cmd)
    return json.loads(send_ui_service_cmd_get_res(cmd))


def send_cmd_get_res_data(_cmd, port):
    _cmd['Params']['TestPort'] = int(port)
    with allure.step('发送的命令为：{0}'.format(_cmd)):
        res_data = send_cmd(_cmd)
    with allure.step('命令的返回值为：{0}'.format(res_data)):
        print('{0} cmd_res：{1}'.format(_cmd['API'], res_data))
    with check.check:
        with allure.step('断言 {0} 命令返回数据code，期望值：0，实际值：{1}'.format(_cmd['API'], res_data['Code'])):
            assert 0 == res_data['Code']
    return res_data['Data']


def send_cmd_get_res_need_point(_cmd, port, cur_point):
    _cmd['Params']['PointIndex'] = cur_point - 1
    _cmd['Params']['TestPort'] = int(port)
    with allure.step('发送 {0} 命令'.format(_cmd['API'])):
        with allure.step('_cmd：{0}'.format(_cmd)):
            res_data = send_cmd(_cmd)
        with allure.step('命令返回数据为：{0}'.format(res_data)):
            print('{0} 命令返回数据为：{1}'.format(_cmd['API'], res_data))
        with check.check:
            with allure.step('断言 {0} 命令返回数据code，期望值：0，实际值：{1}'.format(_cmd['API'], res_data['Code'])):
                assert 0 == res_data['Code']
    return res_data['Data']


def data_set_related_check_code(res_data, cmd_key):
    cmd_res_code = res_data['Code']
    with allure.step('断言 {0} 命令返回值 Code， 期望值：0，实际值：{1}'.format(cmd_key, cmd_res_code)):
        assert 0 == cmd_res_code


def data_set_related_check_res(res_data, port, cmd_key):
    change_dict = {'FileInfo': 'file_info', 'StartWork': 'start_work', 'RegisterParmeter': 'register_parameter',
                   'UnRegisterParmeter': 'unregister_parameter', 'StopWork': 'stop_work',
                   'GetMessageDirection': 'get_msg_code_direction'}
    if isinstance(res_data['Data'], str):
        data = json.loads(res_data['Data'])
    else:
        data = res_data['Data']

    if 'Items' in data.keys():
        for item_data in data['Items']:
            devId = item_data['devId']
            res_port = item_data['port']
            with check.check:
                with allure.step(
                        '断言 {0} 命令返回值 devId， 期望值：{1}，实际值：{2}'.format(cmd_key, TestUIService.device_id,
                                                                                  devId)):
                    assert devId == TestUIService.device_id
                with allure.step('断言 {0} 命令返回值 port， 期望值：{1}，实际值：{2}'.format(cmd_key, port, res_port)):
                    assert res_port == int(port)
    else:
        get_port = data['test_port']
        req_data = data['req']
        with check.check:
            with allure.step('断言命令返回值 port， 期望值：{0}，实际值：{1}'.format(port, get_port)):
                assert get_port == int(port)
            with allure.step(
                    '断言 {0} 命令返回值 req， 期望值：{1}，实际值：{2}'.format(cmd_key, change_dict[cmd_key], req_data)):
                assert change_dict[cmd_key] == req_data


def wait_test_complete(hash_key):
    # 等待测试完成
    cr_count = 0
    star_time = time.time()
    while True:
        total_parallel_group_count = f_redis.hget(hash_key, 'total_parallel_group_count')
        finished_parallel_group_count = f_redis.hget(hash_key, 'finished_parallel_group_count')
        total_group_count = f_redis.hget(hash_key, 'total_group_count')
        finished_group_count = f_redis.hget(hash_key, 'finished_group_count')
        if time.time() - star_time >= 3600:
            with allure.step(
                    '等待业务完成time out， 当前的total_parallel_group_count为： {0}， finished_parallel_group_count为：{1}'.format(
                        total_parallel_group_count, finished_parallel_group_count)):
                print('等待业务完成time out')
                break
        if total_parallel_group_count and finished_parallel_group_count and total_group_count and finished_group_count:
            if finished_parallel_group_count == total_parallel_group_count and finished_group_count == total_group_count:
                print('success, 整个业务结束')
                break
            else:
                cr_count += 1
                print('第{0}次检测，业务还在进行中，等待五秒后再次检查'.format(cr_count))
                time.sleep(5)
        else:
            print('total_parallel_group_count: ', total_parallel_group_count)
            print('finished_parallel_group_count: ', finished_parallel_group_count)
            print('finished_group_count: ', finished_group_count)
            print('total_group_count: ', total_group_count)
            time.sleep(10)


def update_test_plan(test_plan_id):
    get_test_plan_cmd = 'select "test_plan_data"."test_plan_xml" from ' \
                        '"public"."test_plan_data" WHERE ' \
                        '"test_plan_data"."id" = {0}'.format(test_plan_id)
    print('get_test_plan_cmd: ', get_test_plan_cmd)
    serial_test_plan_data = pg_project.pg_run_sql_fetchall(get_test_plan_cmd)

    pg_insert_cmd = 'INSERT INTO "public"."testplan_history" (unified_xml, dev_id) VALUES (\'{0}\', \'{1}\')'.format(
        serial_test_plan_data[0][0], TestUIService.device_id)
    pg_project.pg_insert_data(pg_insert_cmd)


@allure.feature("UIService 测试")
class TestUIService:
    device_id = None

    def setup_class(self):
        with allure.step('获取可以使用的模块端口'):
            TestUIService.device_id = get_device_id_from_redis()
            print('device_id: ', TestUIService.device_id)

            dev_hash_name = get_all_run_process(TestUIService.device_id)
            TestUIService.test_port_list = check_module(dev_hash_name)

            with allure.step('期望值：值不为空，实际值：{0}'.format(TestUIService.test_port_list)):
                print('TestUIService.test_port_list: ', TestUIService.test_port_list)
                assert TestUIService.test_port_list

        with allure.step('连接UIService'):
            websocket_status = ui_service_project.connect()
            with check.check:
                with allure.step('断言 UIService 的连接状态是否为101. {0}'.format(websocket_status == 101)):
                    assert websocket_status == 101

    def teardown_class(self):
        ui_service_project.disconnect()

    @allure.step('业务相关接口测试')
    def test_task_related_interface(self):
        update_test_plan(test_plan_id=17)

        cmd_dict = {
            'UpdateTestplan': {"API": "UpdateTestplan",
                               "Params": {"Name": "", "TimeZone": "", "TestPlanXml": "", "Origin": 0, "TestPort": 2,
                                          "RequestId": "", "IsTest": True}},
            'StartTestPlan': {"API": "StartTestPlan",
                              "Params": {'TestPort': 2, 'RequestId': '', 'FileName': '', 'IsFileCut': 0}},
            'StopTestPlan': {"API": "StopTestPlan",
                             "Params": {'TestPort': 2, 'RequestId': '', 'FileName': '', 'IsFileCut': 0}},
            'GetTestPlanStatus': {"API": "GetTestPlanStatus", "Params": {"TestPort": 2, "RequestId": ""}},
            'PauseTestPlan': {"API": "PauseTestPlan",
                              "Params": {'TestPort': 2, 'RequestId': '', 'FileName': '', 'IsFileCut': 0}},
        }
        status_swap_dict = {'FinishedGroupCount': 'finished_group_count', 'TotalGroupCount': 'total_group_count',
                            'FinishedParallelGroupCount': 'finished_parallel_group_count',
                            'TotalParallelGroupCount': 'total_parallel_group_count'}
        run_sequence_list = ['UpdateTestplan', 'StartTestPlan', 'PauseTestPlan', 'StopTestPlan']
        change_dict = {'UpdateTestplan': 'Preparing', 'StartTestPlan': 'Testing', 'PauseTestPlan': 'Paused',
                       'StopTestPlan': 'Stopped'}

        print('TestUIService.test_port_list: ', TestUIService.test_port_list)
        for test_port in TestUIService.test_port_list:
            with allure.step('当前测试端口为：{0}'.format(test_port)):
                schedule_hash_key = TestUIService.device_id + '-DCSTestSchedule-' + str(test_port)
                for cmd_key in run_sequence_list:
                    with allure.step('发送 {0} 命令'.format(cmd_key)):
                        res_data = json.loads(send_cmd_get_res_data(cmd_dict[cmd_key], test_port))
                        if 'UpdateTestplan' == cmd_key:
                            time.sleep(1)
                        elif 'PauseTestPlan' == cmd_key:
                            time.sleep(4)
                        else:
                            time.sleep(1)
                        if -1 == res_data['status']:
                            with check.check:
                                with allure.step('命令：{0}，返回状态为：{1}'.format(cmd_key, res_data['status'])):
                                    assert 0 == res_data['status']
                        else:
                            test_status = f_redis.hget(schedule_hash_key, 'test_status')
                            with allure.step('断言 {0} 中的test_status '.format(schedule_hash_key)):
                                with check.check:
                                    with allure.step('期望值：{0}，实际值：{1}'.format(change_dict[cmd_key], test_status)):
                                        assert change_dict[cmd_key] == test_status
                            if 'PauseTestPlan' == cmd_key:
                                cmd_res = send_cmd_get_res_data(cmd_dict['GetTestPlanStatus'], test_port)
                                print('cmd_res：', cmd_res)
                                redis_data = f_redis.hgetall(schedule_hash_key)
                                print('redis_data：', redis_data)
                                if 'finished_group_count' in redis_data:
                                    for res_key in cmd_res:
                                        if 'TestPlanStatuses' != res_key:
                                            with check.check:
                                                with allure.step('断言 {0} 期望值：{1}，实际值：{2}'.format(res_key,
                                                                                                         redis_data[
                                                                                                             status_swap_dict[
                                                                                                                 res_key]],
                                                                                                         cmd_res[
                                                                                                             res_key])):
                                                    assert int(redis_data[status_swap_dict[res_key]]) == cmd_res[
                                                        res_key]

    @allure.step('控制相关接口测试')
    def test_control_related_interface(self):
        at_cmd = {"API": "ATCmd", "Params": {"TestPort": 2, "RequestId": "", "ATCmdStr": "AT+CGSN"}}
        for port in TestUIService.test_port_list:
            hash_key = TestUIService.device_id + '-DCSDeviceServer-' + str(port)
            with allure.step('读取redis中端口 {0} hash_key:{1} 的数据'.format(port, hash_key)):
                hash_data = f_redis.hgetall(hash_key)
                with allure.step('redis中读取到的数据为：{0}'.format(hash_data)):
                    print('hash_data: ', hash_data)
            at_cmd['Params']['TestPort'] = int(port)
            with allure.step('发送 ATCmd 命令: {0}'.format(at_cmd)):
                print('at_cmd: ', at_cmd)
                cmd_res = json.loads(send_ui_service_cmd_get_res(at_cmd))
                with allure.step('命令返回的数据为：{0}'.format(cmd_res)):
                    print('cmd_res: ', cmd_res)
            if hash_data['module_imei']:
                with check.check:
                    with allure.step('对比 ATcmd 返回的 imei 和 redis 中读取到的imei， 期望值：{0}，实际值：{1}'.format(
                            hash_data['module_imei'],
                            cmd_res['Data'])):
                        if hash_data['module_imei'] and cmd_res['Data']:
                            assert hash_data['module_imei'] in cmd_res['Data']
                        else:
                            assert hash_data['module_imei']
            else:
                with check.check:
                    with allure.step('ATcmd 返回数据， 期望值：不为空，实际值：{0}'.format(cmd_res['Data'])):
                        assert cmd_res['Data']

    @allure.step('设备相关接口测试')
    def test_device_related_interface(self):
        get_online_device = {"API": "GetOnLineDevice", "Params": {'RequestId': ''}}
        with allure.step('发送 GetOnLineDevice 命令: {0}'.format(get_online_device)):
            cmd_res = json.loads(send_ui_service_cmd_get_res(get_online_device))
            with allure.step('命令返回的数据为：{0}'.format(cmd_res)):
                print('cmd_res: ', cmd_res)
        with allure.step('数据对比'):
            for port in TestUIService.test_port_list:
                print('port: ', port)
                hash_key = TestUIService.device_id + '-DCSDeviceServer-' + str(port)
                with allure.step('读取redis中端口 {0} Hash_key:{1} 的数据'.format(port, hash_key)):
                    hash_data = f_redis.hgetall(hash_key)
                    with allure.step('redis中读取到的数据为:{0}'.format(hash_data)):
                        print('hash_data: ', hash_data)
                with allure.step('对比reids读取到的数据和命令返回的数据'):
                    check_ui_service_cmd_res(cmd_res, hash_data, port)

    @allure.step('数据相关接口测试')
    def test_dataset_related_interface(self):
        data_set_cmd_dict = {
            'FileInfo': {"API": "FileInfo",
                         "Params": {"StrategyType": 0, "FileList": [{"FileType": 0}], "StrategyStatus": 1,
                                    "StrategyTime": 60,
                                    "StrategySize": 0, "TestPort": 8, "RequestId": ""}},
            'GetEventList': {"API": "GetEventList",
                             "Params": {"TestPort": 4, "RequestId": "", "StartId": 0, "StartPointIndex": 0,
                                        "EndPointIndex": 50,
                                        "Count": 50}},
            'StartWork': {"API": "StartWork",
                          "Params": {"FileName": "", "IsFileCut": 0, "TestPort": 8, "RequestId": ""}},
            'GetCurrentLogDataFiles': {"API": "GetCurrentLogDataFiles", "Params": {"RequestId": ""}},
            'GetMessageCode': {"API": "GetMessageCode", "Params": {"TestPort": 2, "RequestId": "", "PointIndex": 0}},
            'GetMsgCodeInfo': {"API": "GetMsgCodeInfo",
                               "Params": {"TestPort": 2, "RequestId": "", "PointIndex": 0, "IsUtcTime": 0,
                                          "IsHandsetTime": 0}},
            'GetNextMsgCodeIndex': {"API": "GetNextMsgCodeIndex",
                                    "Params": {"TestPort": 4, "RequestId": "", "PointIndex": 0, "MsgCode": 0,
                                               "IsDown": 1}},
            'GetMultiMsgCodeInfo': {"API": "GetMultiMsgCodeInfo",
                                    "Params": {"TestPort": 8, "RequestId": "", "StartPointIndex": 0,
                                               "EndPointIndex": 20}},
            'GetParamInt64Value': {"API": "GetParamInt64Value",
                                   "Params": {"TestPort": 4, "RequestId": "", "PointIndex": 0, "ParamCode": 2131165187,
                                              "Filter": 0}},
            'GetParamRealTime': {"API": "GetParamRealTime",
                                 "Params": {"TestPort": 4, "RequestId": "", "ParamCode": 0}},
            'GetMessageDirection': {"API": "GetMessageDirection",
                                    "Params": {'TestPort': 2, 'RequestId': '', 'PointIndex': 0}},
            'RegisterParmeter': {"API": "RegisterParmeter",
                                 "Params": {"TestPort": 4, "RequestId": "", "ParamCodes": [2132615169]}},
            'GetPointIndexTime': {"API": "GetPointIndexTime",
                                  "Params": {"TestPort": 4, "RequestId": "", "PointIndex": 0, "IsUtcTime": 1,
                                             "IsHandsetTime": 0, }},
            'GetTotalPointCount': {"API": "GetTotalPointCount", "Params": {"TestPort": 8, "RequestId": ""}},
            'StopWork': {"API": "StopWork",
                         "Params": {"FileName": "", "IsFileCut": 1, "TestPort": 0, "RequestId": ""}},
            'UnRegisterParmeter': {"API": "UnRegisterParmeter",
                                   "Params": {"TestPort": 4, "RequestId": "", "ParamCodes": [2131165187]}}
        }

        for port in TestUIService.test_port_list:
            # 注册参数
            with allure.step('当前测试端口为：{0}'.format(port)):
                with allure.step('注册Current Network Type参数'):
                    # print('发送 RegisterParmeter 命令')
                    regis_res = send_cmd_get_res_data(data_set_cmd_dict['RegisterParmeter'], port)
                    print('regis_res：', regis_res)

                with allure.step('设置数据文件'):
                    file_info_res = send_cmd_get_res_data(data_set_cmd_dict['FileInfo'], port)
                    print('file_info_res：', file_info_res)

                with allure.step('发送start_work'):
                    start_res = send_cmd_get_res_data(data_set_cmd_dict['StartWork'], port)
                    print('start_res：', start_res)

                # 获取当前采样点
                with allure.step('获取当前采样点'):
                    cur_point = send_cmd_get_res_data(data_set_cmd_dict['GetTotalPointCount'], port)
                    print('cur_point：', cur_point)
                    with allure.step('当前采样点为：{0}'.format(cur_point)):
                        assert cur_point

                # 获取事件列表
                with allure.step('获取事件列表'):
                    data_set_cmd_dict['GetEventList']['Params']['EndPointIndex'] = cur_point - 1
                    event_count = data_set_cmd_dict['GetEventList']['Params']['Count']
                    event_list = send_cmd_get_res_data(data_set_cmd_dict['GetEventList'], port)
                    print('event_list：', event_list)
                    with check.check:
                        with allure.step(
                                '断言事件列表长度，期望值：{0}，实际值：{1}'.format(event_count, len(event_list['Items']))):
                            assert event_count == len(event_list['Items'])
                    time.sleep(3)

                with allure.step('获取当前采样点 UTC 时间'):
                    cur_point_time = send_cmd_get_res_need_point(data_set_cmd_dict['GetPointIndexTime'], port,
                                                                 cur_point)
                    print('cur_point_time：', cur_point_time)
                    with allure.step('当前采样点的时间为：{0}'.format(cur_point_time)):
                        pass
                        # assert cur_point_time

                # 获取redis中的当前的试试参数，返回redis中的所有值
                with allure.step('获取redis中所有参数以及参数值'):
                    cur_param = send_cmd_get_res_data(data_set_cmd_dict['GetParamRealTime'], port)
                    with allure.step('GetParamRealTime 命令值：{0}'.format(cur_param)):
                        print('GetParamRealTime 命令值：{0}'.format(cur_param))

                    parameter_table_hash_key = TestUIService.device_id + '-DCSDataSets-' + str(
                        port) + '-parameter_table'
                    parameter_table_data = f_redis.hgetall(parameter_table_hash_key)
                    for i in parameter_table_data:
                        parameter_table_data[i] = int(parameter_table_data[i])
                    with allure.step('redis返回的数据为：{0}'.format(parameter_table_data)):
                        print('redis返回的数据为：{0}'.format(parameter_table_data))

                    cnt = 0
                    for i_key in parameter_table_data:
                        if parameter_table_data[i_key] == cur_param[i_key]:
                            cnt += 1
                    with check.check:
                        with allure.step('总参数值个数为：{0}，相同参数值个数为：{1}，期望值：两个数差值在 5 以内'.format(len(parameter_table_data), cnt)):
                            assert len(parameter_table_data) - cnt < 5


                # 获取当前采样点
                with allure.step('获取指定参数的参数值'):
                    need_parameter_data = f_redis.hget(parameter_table_hash_key, '2131165187')
                    with allure.step('从redis中读取 key:2131165187 的数据为：{0}'.format(need_parameter_data)):
                        pass
                    cur_Int64Value_param = send_cmd_get_res_need_point(data_set_cmd_dict['GetParamInt64Value'], port,
                                                                       cur_point)
                    print('cur_Int64Value_param: ', cur_Int64Value_param)
                    with allure.step('GetParamInt64Value 命令返回的指定参数值为：{0}'.format(cur_Int64Value_param)):
                        assert cur_Int64Value_param

                with allure.step('获取当前数据文件'):
                    redis_hash = TestUIService.device_id + '-DCSDataSets-' + str(port)
                    with allure.step('发送 {0} 命令: {1}'.format(data_set_cmd_dict['GetCurrentLogDataFiles']['API'],
                                                                 data_set_cmd_dict['GetCurrentLogDataFiles'])):
                        print('发送GetCurrentLogDataFiles命令')
                        cur_data_file = send_cmd(data_set_cmd_dict['GetCurrentLogDataFiles'])

                    # 读取redis
                    file_type_0 = f_redis.hget(redis_hash, 'file_type_0')
                    with allure.step('{0} 中读取到的文件信息为：{1}'.format(redis_hash, file_type_0)):
                        print('file_type_0: ', file_type_0)
                    with allure.step('命令返回数据：{0}'.format(cur_data_file)):
                        print('cur_data_file：', cur_data_file)

                    if file_type_0:
                        data_file_name = cur_data_file['Data'][0]['FilePath']
                        check_flag = os.path.exists(data_file_name)
                        with allure.step('断言，当前数据文件是否存在，期望值：True，实际值：{0}'.format(check_flag)):
                            assert check_flag

                # 获取上下行
                with allure.step('获取当前采样点的信令类型'):
                    cur_dir = send_cmd_get_res_need_point(data_set_cmd_dict['GetMessageDirection'], port, cur_point)
                    print('cur_dir：', cur_dir)
                    with allure.step('当前信令类型为：{0}'.format(json.loads(cur_dir)['direction'])):
                        assert json.loads(cur_dir)['direction'] in [0, 1, 2]

                # 获取信令code
                with allure.step('获取当前信令code'):
                    for point in range(1, cur_point):
                        cur_msg_code = send_cmd_get_res_need_point(data_set_cmd_dict['GetMessageCode'], port, point)
                        if cur_msg_code:
                            break
                    print('cur_msg_code：', cur_msg_code)
                    with allure.step('采样点 {0} 的信令为：{1}'.format(point - 1, cur_msg_code)):
                        assert cur_msg_code

                with allure.step('获取采样点 {0} 的信令信息'.format(cur_point - 1)):
                    cur_msg_code_info = send_cmd_get_res_need_point(data_set_cmd_dict['GetMsgCodeInfo'], port,
                                                                    cur_point)
                    print('cur_msg_code_info：', cur_msg_code_info)
                    with allure.step('信令信息为：{0}'.format(cur_msg_code_info)):
                        assert cur_msg_code_info

                # 获取code的下一个采样点
                data_set_cmd_dict['GetNextMsgCodeIndex']['Params']['MsgCode'] = cur_msg_code
                next_point_index = send_cmd_get_res_need_point(data_set_cmd_dict['GetNextMsgCodeIndex'], port,
                                                               cur_point)
                print('next_point_index：', next_point_index)

                # 注销参数
                with allure.step('注销NR RSRP参数'):
                    # 读取redis中的数据
                    unregister_res = send_cmd_get_res_data(data_set_cmd_dict['UnRegisterParmeter'], port)
                    print('unregis_res：', unregister_res)
                    time.sleep(8)
                    get_redis_data = f_redis.hget(parameter_table_hash_key, '2131165187')
                    with check.check:
                        with allure.step('断言注销的参数在parameter_table redis中不存在，期望值：-9999，实际值：{0}'.format(
                                get_redis_data)):
                            assert '-9999' == get_redis_data

                with allure.step('发送stop_work'):
                    stop_res = send_cmd_get_res_data(data_set_cmd_dict['StopWork'], port)
                    print('stop_res：', stop_res)


if __name__ == "__main__":
    pass

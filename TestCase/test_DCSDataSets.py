import ctypes
import random
import threading
import time
from ctypes import *
import os

import allure
import pytest
import sys
import json
import csv

import pytz
from pytest_check import check
from Common.GobalVariabies import *
from Common.Operation import *
from pynng import nng

sys.path.append("..")


@allure.feature("数据集服务测试用例")
class TestDCSDataSets:
    ui_service_project = None
    max_standard_value = {'167789824': 7783, '167789832': 4, '167789849': 1, '167789856': 2, '167789867': 2,
                          '167789886': 122786, '167789887': 5750, '167789899': 15000, '167789904': 0,
                          '167789905': 27000, '167789962': 3408960, '167793688': 18528, '167793689': 18432,
                          '167793692': 34579, '167793693': 34023, '167813121': 144896, '167813122': 1127785,
                          '167813123': 144896, '167813124': 340198, '2131165184': 20, '2131165187': -6710,
                          '2131165188': -1029, '2131165190': 36214, '2131165192': 627264, '2131165199': 1667,
                          '2131165214': 2000, '2131165224': 20, '2131165225': 7, '2131165240': 20, '2131165241': 221,
                          '2131165277': 6000, '2131165278': 5000}

    min_standard_value = {'167789824': 7783, '167789832': 3, '167789849': 1, '167789856': 2, '167789867': 2,
                          '167789886': 4000, '167789887': 4000, '167789899': 13000, '167789904': 0, '167789905': 11000,
                          '167789962': 3408960, '167793688': 0, '167793689': 0, '167793692': 0, '167793693': 0,
                          '167813121': 1864, '167813122': 0, '167813123': 1864, '167813124': 0, '2131165184': 20,
                          '2131165187': -8427, '2131165188': -1041, '2131165190': 23494, '2131165192': 627264,
                          '2131165199': 0, '2131165214': 0, '2131165224': 4, '2131165225': -2, '2131165240': 1,
                          '2131165241': 1, '2131165277': 0, '2131165278': 0}

    avg_standard_value = {'167789824': 7783.0, '167789832': 3.659090909090909, '167789849': 1.0, '167789856': 2.0,
                          '167789867': 2.0, '167789886': 56319.70124481328, '167789887': 4097.813636363637,
                          '167789899': 14121.690625, '167789904': 0.0, '167789905': 21569.162895927602,
                          '167789962': 3408960.0, '167793688': 5178.467692307692, '167793689': 5150.950769230769,
                          '167793692': 13016.415384615384, '167793693': 12836.236923076924,
                          '167813121': 45136.23170731707, '167813122': 180827.50461538462,
                          '167813123': 45115.939024390245, '167813124': 59808.42153846154, '2131165184': 20.0,
                          '2131165187': -7455.926470588235, '2131165188': -1033.9588235294118,
                          '2131165190': 29978.47156862745, '2131165192': 627264.0, '2131165199': 6.776422764227642,
                          '2131165214': 8.130081300813009, '2131165224': 15.757322175732218, '2131165225': 2.88,
                          '2131165240': 8.695454545454545, '2131165241': 58.92116182572614,
                          '2131165277': 2567.4615384615386, '2131165278': 1355.5726495726497}

    times_standard_value = {'167789824': 1020, '167789832': 220, '167789849': 241, '167789856': 220, '167789867': 241,
                            '167789886': 241, '167789887': 220, '167789899': 320, '167789904': 218, '167789905': 221,
                            '167789962': 1020, '167793688': 325, '167793689': 325, '167793692': 325, '167793693': 325,
                            '167813121': 246, '167813122': 325, '167813123': 246, '167813124': 325, '2131165184': 1020,
                            '2131165187': 1020, '2131165188': 1020, '2131165190': 1020, '2131165192': 1020,
                            '2131165199': 246, '2131165214': 246, '2131165224': 239, '2131165225': 325,
                            '2131165240': 220, '2131165241': 241, '2131165277': 234, '2131165278': 234}

    def setup_class(self):
        TestDCSDataSets.package_project = PackageUnpack(dll_path)

        redis_host = parse_xml_get_common(config_xml_path)
        print('redis_host: ', redis_host)
        TestDCSDataSets.data_set_hash_key = get_device_id_from_redis() + '-DCSDataSets-4'
        TestDCSDataSets.redis_chanel = TestDCSDataSets.data_set_hash_key + '-cmdrequest'
        print('channel: ', TestDCSDataSets.redis_chanel)

        pubsub.subscribe('PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest-cmdrequest')

        with allure.step('获取测试端口和设备id'):
            clear_dcs_service()
            datasets_service_config_xml = os.path.join(xml_path, 'DCSServerMgrcfg_DCSDataSets.xml')
            with allure.step('启动数据集测试管理和数据服务'):
                print('启动数据集服务，并等待 5s......')
                start_service(exe_path, datasets_service_config_xml)
                time.sleep(5)

            # 从redis中获取数据集nng的push端口
            TestDCSDataSets.data_set_push_port = f_redis.hget(TestDCSDataSets.data_set_hash_key, 'pull_port')
            print('data_set_push_port: ', TestDCSDataSets.data_set_push_port)

            with allure.step('初始化数据集服务'):
                print('发送初始化命令，初始化数据集服务')
                cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                            'method': 'decode_init',
                            'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSTestMgr-10',
                            'test_port': 4,
                            'device_id': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai',
                            'device_model': 'FIBOCOM FM160'}

                print('redis_chanel: ', TestDCSDataSets.redis_chanel)
                pub_json_cmd_to_redis_chanel(TestDCSDataSets.package_project, cmd_json, pubsub,
                                                   TestDCSDataSets.redis_chanel)

        with allure.step('连接UIService'):
            TestDCSDataSets.ui_service_project = WebSocket('ws://127.0.0.1:2022/')
            websocket_status = TestDCSDataSets.ui_service_project.connect()
            with check.check:
                with allure.step('断言 UIService 的连接状态是否为101. {0}'.format(websocket_status == 101)):
                    assert websocket_status == 101

    def teardown_class(self):
        pubsub.unsubscribe('PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest-cmdrequest')

        with allure.step('数据集服务测试完成，清理数据集测试相关服务'):
            print('清理所有服务')
            clear_dcs_service()
        time.sleep(1)
        with allure.step('正常启动所有服务'):
            print('正常启动所有服务', exe_path)
            start_service(exe_path, config_xml_path)
            print('数据集测试结束，正常启动所有服务，等待 20s ......')
            time.sleep(20)

    @allure.step("DCSDataSets数据推送测试")
    def test_push_original_data(self):
        with allure.step('当前测试端口为：4'):
            print('当前测试端口为：4')
        data_path = os.path.join(PROJECT_BASE, r'TestData\qmdl_data')
        test_file = 'test_iperf.qmdl'
        with allure.step('调用 send_start_work_cmd接口，发送 start_work 命令，给端口：4 的数据集服务'):
            print('发送 start work 命令')
            self.send_start_work_cmd()
            time.sleep(1)
        with allure.step('推送原始数据给数据集，推送文件为：{0}'.format(test_file)):
            print('推送原始数据给数据集')
            self.read_qmdl_and_send_to_DCSDataSets(os.path.join(data_path, test_file))
            time.sleep(1.5)
        with allure.step('发送命令给数据集服务，查询对比参数值'):
            self.query_comparison_param_value()
        print('获取指定采样点的指定参数')
        self.query_param_value_by_point(2131165278, 18236)
        # with allure.step('发送命令给数据集服务，查询对比事件'):
        #     self.query_comparison_event_value()
        with allure.step('调用接口send_stop_work_cmd，发送 stop_work 命令，给端口：4 的数据集服务'):
            print('发送 stop_work 命令')
            self.send_stop_work_cmd()

    def send_start_work_cmd(self):
        ddib_path = os.path.join(local_tmp_path, 'DCSDataSets_auto_test')
        if os.path.exists(ddib_path + '.ddib'):
            os.remove(ddib_path + '.ddib')

        cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                    'method': 'start_work',
                    'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiAutoTest',
                    'test_port': 4,
                    'file_name': os.path.join(local_tmp_path, 'DCSDataSets_auto_test')}

        pub_json_cmd_to_redis_chanel(TestDCSDataSets.package_project, cmd_json, pubsub,
                                     TestDCSDataSets.redis_chanel)

    def send_stop_work_cmd(self):
        cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                    'method': 'stop_work',
                    'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSTestMgr-10',
                    'test_port': 4}

        pub_json_cmd_to_redis_chanel(TestDCSDataSets.package_project, cmd_json, pubsub,
                                     TestDCSDataSets.redis_chanel)

    def read_qmdl_and_send_to_DCSDataSets(self, qmdl_file):
        data_set_push_channel = 'tcp://127.0.0.1:' + str(TestDCSDataSets.data_set_push_port)
        with allure.step('当前数据集 nng 通道为：{0}'.format(data_set_push_channel)):
            print('data_set_push_channel: ', data_set_push_channel)
        push_sock = nng.Push0(dial=data_set_push_channel)
        cmd_json = {'method': 'original_data', 'params': {'data_flag': 0, 'utc_time': 0}, 'reqid': '1234',
                    'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest-4'}
        cmd_json['params']['data_flag'] = 68
        with open(qmdl_file, 'rb') as f:
            cnt = 0
            # for i in range(10):
            while True:
                cmd_json['params']['utc_time'] = time.time().__round__()
                chunk_size = random.randint(3800000, 4000000)
                data = f.read(chunk_size)
                if not data:
                    break
                cnt += 1
                packed_json = TestDCSDataSets.package_project.package_json(json.dumps(cmd_json), data)
                push_sock.send(packed_json)
                time.sleep(0.1)
                print('**' * 50)
            with allure.step('发送了 {0} 次，文件 {1}，发送完成'.format(cnt, qmdl_file)):
                print('文件 {0}，发送完成'.format(qmdl_file))

    def deal_event_res_data(self, event_code_list, event_data, event_count_dict):
        print('event_data: ', event_data['params'].__len__())
        # 获取指定的事件
        for params_content in event_data['params'] if event_data['params'].__len__() else range(1, 1):
            if params_content['event_flag'] in event_code_list:
                if params_content['event_flag'] in event_count_dict:
                    event_count_dict[params_content['event_flag']] += 1
                else:
                    event_count_dict[params_content['event_flag']] = 1

    def query_comparison_event_value(self):
        event_count_dict = {}
        event_code_list = [0x30170, 0x30171, 0x30172, 0x30173, 0x30180, 0x30180, 0x30181, 0x30182, 0x30183, 0x131,
                           0x132, 0x135, 0x136, 0x80, 0x88, 0x82, 0x83, 0x85, 0xE02, 0xE03, 0xE08, 0xE09, 0xE06,
                           0x190, 0x192]

        cmd_json_mould = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                          'method': 'get_total_point_count',
                          'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSTestMgr-10',
                          'test_port': 4}
        cur_point_count = pub_json_cmd_to_redis_chanel(TestDCSDataSets.package_project, cmd_json_mould, pubsub,
                                                       TestDCSDataSets.redis_chanel)['total_point_count']
        with allure.step('总采样点：{0}'.format(cur_point_count)):
            point_list = self.split_number(cur_point_count)

        # 查询事件
        with allure.step('发送查询事件命令给数据集'):
            cmd_json_mould['method'] = 'get_multi_event_info'
            for point_range in point_list:
                with allure.step('当前查询的起始采样点为：{0}，结束采样点为{1}'.format(point_range[0], point_range[1])):
                    cmd_json_mould['start_point_index'] = point_range[0]
                    cmd_json_mould['end_point_index'] = point_range[1]
                event_data = pub_json_cmd_to_redis_chanel(TestDCSDataSets.package_project, cmd_json_mould, pubsub,
                                                          TestDCSDataSets.redis_chanel)
                self.deal_event_res_data(event_code_list, event_data, event_count_dict)
                with allure.step('当前查询返回的事件结果为：{0}'.format(event_count_dict)):
                    print('当前查询返回的事件结果为：{0}'.format(event_count_dict))
            cmd_json_mould.pop('start_point_index', None)
            cmd_json_mould.pop('end_point_index', None)

        with allure.step('分析数据集返回的事件信息'):
            if event_count_dict:
                with allure.step('获取到相关事件为:{0}'.format(event_count_dict)):
                    print('事件字典为：', event_count_dict)
            else:
                with check.check:
                    with allure.step('failed,未获取到相关事件，事件为:{0}'.format(event_count_dict)):
                        assert event_count_dict

    def query_param_value_by_point(self, param_key, point_index):
        cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                    'method': 'get_multi_param_info',
                    'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSTestMgr-10',
                    'test_port': 4, 'start_point_index': point_index, 'end_point_index': point_index + 1,
                    'params': [param_key]}
        cmd_res = pub_json_cmd_to_redis_chanel(TestDCSDataSets.package_project, cmd_json, pubsub,
                                               TestDCSDataSets.redis_chanel)['params']
        print('采样点：{0} 的参数值为：{1}'.format(point_index, cmd_res))

    def query_comparison_param_value(self):
        cmd_json_mould = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                          'method': 'get_total_point_count',
                          'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSTestMgr-10',
                          'test_port': 4}

        cur_point_count = pub_json_cmd_to_redis_chanel(TestDCSDataSets.package_project, cmd_json_mould, pubsub,
                                                       TestDCSDataSets.redis_chanel)['total_point_count']
        with check.check:
            with allure.step('获取总采样点，期望值：18617，实际值：{0}'.format(cur_point_count)):
                print('total_point：', cur_point_count)
                assert 18617 == cur_point_count
        point_list = self.split_number(cur_point_count)
        print('point_list: ', point_list)

        with allure.step('查询参数，计算参数的最值、均值和次数'):
            param_list = [2132615169, 2131165187, 0x7F070004, 2131165190, 2131099662, 0x7F06000F, 2131099649,
                          0x7F1D2001,
                          0x7F1D200D, 0x7F07007A, 0x7F07007B, 0x7F07007D, 0x7F07000A, 0xA00455C, 0x7F070078, 0x7F070079,
                          0xA00458A, 0x7F070008, 0x7F070000, 0x7F070009, 0x7F070017,
                          0xA004500,
                          0xA004501,
                          0x7F07000C,
                          0x7F07000B,
                          0x7F07004D,
                          0x7F070041,
                          0x1A100701,
                          0x7F070044,
                          0x7F070049,
                          0x1A100702,
                          0x7F070046,
                          0x7F07004B,
                          0xA004520,
                          0xA00452B,
                          0x7F070038,
                          0x7F070039,
                          0xA00454B,
                          0x7F07002A,
                          0x7F070029,
                          0x7F070028,
                          0xA004508,
                          0xA004519,
                          0xA00453F,
                          0xA00453E,
                          0xA004551,
                          0xA004550,
                          0x7F07000F,
                          0x7F07005D,
                          0x7F07001E,
                          0x7F07005E,
                          0xA002151,
                          0xA002153,
                          0xA005419,
                          0xA005418,
                          0xA00A003,
                          0xA00A001,
                          0xA00541D,
                          0xA00541C,
                          0xA00A004,
                          0xA00A002,
                          0xA00106F,
                          0xA005023,
                          0xA005401,
                          0xA005400,
                          0x7F070062,
                          ]

            times_dict = {}
            res_dict = {}
            max_dict = {}
            min_dict = {}
            avg_dict = {}
            res_times_dict = {}

            for point_range in point_list:
                cmd_json_get_param = {
                    'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                    'method': 'get_multi_param_info',
                    'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSTestMgr-10',
                    'test_port': 4, 'start_point_index': point_range[0], 'end_point_index': point_range[1],
                    'params': param_list}

                cmd_res = pub_json_cmd_to_redis_chanel(TestDCSDataSets.package_project, cmd_json_get_param, pubsub,
                                                       TestDCSDataSets.redis_chanel)['params']
                print('cmd_res: ', cmd_res)
                for i_res in cmd_res:
                    for i_key in i_res:
                        if i_key in res_dict:
                            res_dict[i_key] = res_dict[i_key] + i_res[i_key]
                        else:
                            res_dict[i_key] = i_res[i_key]
                        # 计算次数
                        if i_key in times_dict:
                            times_dict[i_key] += len(i_res[i_key])
                        else:
                            times_dict[i_key] = len(i_res[i_key])
                        print('code: {0}, tims: {1}'.format(i_key, len(i_res[i_key])))
            print('res_dict: ', res_dict)

            # 计算最大值
            for i_code_res in res_dict:
                print('i_code_res: ', i_code_res)
                max_val = max(sub_lst[1] for sub_lst in res_dict[i_code_res])
                avg_val = sum(sub_lst[1] for sub_lst in res_dict[i_code_res]) / len(res_dict[i_code_res])
                min_val = min(sub_lst[1] for sub_lst in res_dict[i_code_res])
                print('max_val: ', max_val)
                print('min_val: ', min_val)
                print('avg_val: ', avg_val)
                print('times: ', len(res_dict[i_code_res]))
                max_dict[i_code_res] = max_val
                min_dict[i_code_res] = min_val
                avg_dict[i_code_res] = avg_val
                res_times_dict[i_code_res] = len(res_dict[i_code_res])

            with allure.step('参数最大值对比'):
                print('max_dict: ', max_dict)
                for param_key in max_dict:
                    stand_value = TestDCSDataSets.max_standard_value[param_key]
                    check_value = max_dict[param_key]
                    with check.check:
                        with allure.step(
                                '对比参数 {0}，期望值：{1}，实际值：{2}'.format(param_key, stand_value, check_value)):
                            assert stand_value == check_value

            with allure.step('参数最小值对比'):
                print('min_dict: ', min_dict)
                for param_key in min_dict:
                    stand_value = TestDCSDataSets.min_standard_value[param_key]
                    check_value = min_dict[param_key]
                    with check.check:
                        with allure.step(
                                '对比参数 {0}, 期望值：{1}，实际值：{2}'.format(param_key, stand_value, check_value)):
                            assert check_value == stand_value

            with allure.step('参数均值对比'):
                print('avg_dict: ', avg_dict)
                for param_key in avg_dict:
                    stand_value = TestDCSDataSets.avg_standard_value[param_key]
                    check_value = avg_dict[param_key]
                    with check.check:
                        with allure.step(
                                '对比参数 {0}, 期望值：{1}，实际值：{2}'.format(param_key, stand_value, check_value)):
                            assert check_value == stand_value

            with allure.step('参数出现总次数对比'):
                print('times_dict: ', times_dict)
                for param_key in times_dict:
                    stand_value = TestDCSDataSets.times_standard_value[param_key]
                    check_value = times_dict[param_key]
                    with check.check:
                        with allure.step(
                                '对比参数 {0}, 期望值：{1}，实际值：{2}'.format(param_key, stand_value, check_value)):
                            assert check_value == stand_value

            print('res_times_dict: ', res_times_dict)

            all_header_list = ['参数code', '出现次数', '最大值', '最小值', '均值']
            dict_list = [list(times_dict.items()), max_dict.values(), min_dict.values(), avg_dict.values()]
            df = pd.concat([pd.DataFrame(d) for d in dict_list], ignore_index=True, axis=1)
            csv_path = os.path.join(local_tmp_path, 'datasets_max_min_value.csv')
            with allure.step('参数最值、均值等，生成的结果csv文件为：{0}'.format(csv_path)):
                df.to_csv(csv_path, header=all_header_list, index=False)

    def split_number(self, num):
        result = []
        for i in range(0, num, 4500):
            result.append((i, i + 4499 if i + 4499 < num else num))
        return result


if __name__ == "__main__":
    new_test = TestDCSDataSets()
    new_test.setup_class()
    # 推送数据
    new_test.test_push_original_data()
    print('清理所有服务')
    os.system(r'D:\download\ALL_test\test_scripte\kill.bat')

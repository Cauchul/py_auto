import ctypes
import random
import threading
import time
from ctypes import *
import os

import allure
import allure_pytest.plugin
import pytest
import sys
import json
import csv
import conftest



import pytz
from pytest_check import check
from Common.GobalVariabies import *
from Common.Operation import *
from pynng import nng


sys.path.append("..")


@allure.feature("数据集服务回归测试用例")
class TestDCSDataSets:
    ui_service_project = None
    hash_key_list = []
    data_set_push_port_list = []
    data_path = os.path.join(PROJECT_BASE, r'TestData\qmdl_data')

    # 指定业务事件
    event_code_dict = {
        'test_call': [0x30170, 0x31053, 0x31054, 0x30171],
        'test_ping': [0x0190, 0x0192, 0x0193, 0x03E9, 0x10050, 0x10050],
        'test_iperf': [0xE01, 0xE02, 0xE03, 0xE03, 0xE06, 0xE07, 0xE08, 0xE09],
        'test_lteattach':  [0x0606, 0x0607, 0x0608, 0x20412, 0x20414, 0x20415],
        'test_ftpdown': [0x0080, 0x0081, 0x0082, 0x0083, 0x0084, 0x0085, 0x0086, 0x0087, 0x0088],
        'test_ftpup': [0x0090, 0x0091, 0x0092, 0x0093, 0x0094, 0x0095, 0x0096, 0x1004E, 0x10074],
        'test_nr_registration': [0x131, 0x132, 0x133]
    }
    # 事件字典，包括事件顺序码
    event_dict = {'test_call': {4359: {'event_code': '0x30170', 'event_index': 0},
                                5303: {'event_code': '0x3033A', 'event_index': 4},
                                8656: {'event_code': '0x31054', 'event_index': 22}
                                },
                  'test_ping': {500: {'event_code': '0x31012', 'event_index': 5},
                                2438: {'event_code': '0x31037', 'event_index': 45},
                                6328: {'event_code': '0x3100F', 'event_index': 90}
                                },
                  'test_iperf': {465: {'event_code': '0x31012', 'event_index': 5},
                                 2438: {'event_code': '0x31037', 'event_index': 45},
                                 6328: {'event_code': '0x3100F', 'event_index': 90}
                                 },
                  'test_lteattach': {188: {'event_code': '0x31015', 'event_index': 8},
                                     2069: {'event_code': '0x31030', 'event_index': 28},
                                     2096: {'event_code': '0x31006', 'event_index': 29}
                                     },
                  'test_ftpdown': {465: {'event_code': '0x31012', 'event_index': 5},
                                   2438: {'event_code': '0x31037', 'event_index': 45},
                                   6328: {'event_code': '0x3100F', 'event_index': 90}
                                   },
                  'test_ftpup': {465: {'event_code': '0x31012', 'event_index': 5},
                                 2438: {'event_code': '0x31037', 'event_index': 45},
                                 6328: {'event_code': '0x3100F', 'event_index': 90}
                                 },
                  'test_nr_registration': {416: {'event_code': '0x3100F', 'event_index': 3},
                                           464: {'event_code': '0x31054', 'event_index': 10},
                                           507: {'event_code': '0x3100F', 'event_index': 19}
                                           }
                  }

    event_code_dict_all = {
        'test_call': [{0x30170: 'Dutgoing Call Attempt'}, {0x31053: 'NRRRC Reconfiguration Request'},
                      {0x31054: 'WRRRC Reconfiguration Complete'}, {0x30171: 'Dutgoing Call Setup'}
                      ],
        'test_ping': [{0x0190: 'Ping Start'}, {0x0192: 'Ping Success'}, {0x0193: 'Ping Failure '},
                      {0x03E9: 'Ping Test'}
                      ],
        'test_iperf': [{0xE01: 'Iperf Inited'}, {0xE02: 'Iperf Connect Start'}, {0xE03: 'Iperf Connect Success'},
                       {0xE06: 'Iperf Finished'}, {0xE07: 'Iperf Quit'}, {0xE08: 'Iperf FirstData'}, {0xE09: 'Iperf LastData'}
                       ],
        'test_lteattach':  [{0x0606: 'LTE Attach Start'}, {0x0607: 'LTE Attach Success'}, {0x0608: 'LTE Attach Failed'},
                            {0x20412: 'LTE Attach Request'}, {0x20414: 'LTE Attach Complete'}
                            ],
        'test_ftpdown': [{0x0080: 'FTP Download Connect Start'}, {0x0081: 'FTP Download Send RETA'}, {0x0082: 'FTP Download FirstData'},
                         {0x0083: 'FTP Download LastData'}, {0x0084: 'FTP Download Drop'}, {0x0085: 'FTP Download Disconnect'},
                         {0x0088: 'FTP Download Connect Success'}
                         ],
        'test_ftpup': [{0x0090: 'FTP Upload Connect Start'}, {0x0091: 'FTP Upload send sTOR'}, {0x0092: 'FTP Upload FirstData'},
                       {0x0093: 'FTP Upload LastData'}, {0x0094: 'FTP Upload Drop'}, {0x0095: 'FTP Upload Disconnect'},
                      ],
        'test_nr_registration': [{0x131: 'NR Register Start'}, {0x132: 'NR Register Success'},
                                 {0x133: 'NR Register Failure'}, {0x1302A: 'NR Cell PRACH Request'}]
    }
    # 参数查询标准
    param_res_dict = {'test_call': [{18: [{2131165187: '-6292'}, {0x7F070004: '-1036'}, {2131165190: '41058'}]},
                                    {101: [{2131165187: '-6293'}, {0x7F070004: '-1036'}, {2131165190: '45187'}]},
                                    {14242: [{2131165187: '-6309'}, {0x7F070004: '-1037'}, {2131165190: '36368'}]}
                                    ],
                      'test_ping': [{22: [{2131165187: '-6320'}, {0x7F070004: '-1036'}, {2131165190: '45186'}]},
                                    {13229: [{2131165187: '-6302'}, {0x7F070004: '-1036'}, {2131165190: '39692'}]},
                                    {24794: [{2131165187: '-6336'}, {0x7F070004: '-1035'}, {2131165190: '32047'}]}
                                    ],
                      'test_ftpdown': [{19: [{2131165187: '-7693'}, {0x7F070004: '-1032'}, {2131165190: '33945'}]},
                                     {6913: [{2131165187: '-6297'}, {0x7F070004: '-1036'}, {2131165190: '45183'}]},
                                    {14384: [{2131165187: '-6323'}, {0x7F070004: '-1036'}, {2131165190: '33439'}]}
                                    ],
                      'test_ftpup': [{21: [{2131165187: '-6323'}, {0x7F070004: '-1036'}, {2131165190: '33439'}]},
                                       {103: [{2131165187: '-6313'}, {0x7F070004: '-1037'}, {2131165190: '38746'}]},
                                       {22760: [{2131165187: '-6333'}, {0x7F070004: '-1035'}, {2131165190: '40284'}]}
                                       ],
                      'test_iperf': [{23: [{2131165187: '-7198'}, {0x7F070004: '-1036'}, {2131165190: '33534'}]},
                                       {170: [{2131165187: '-7137'}, {0x7F070004: '-1034'}, {2131165190: '32955'}]},
                                       {14242: [{2131165187: '-7781'}, {0x7F070004: '-1034'}, {2131165190: '24689'}]}
                                       ],
                      'test_lteattach': [{17: [{2131165187: '-6303'}, {0x7F070004: '-1036'}, {2131165190: '41789'}]},
                                     {221: [{2131165187: '-6299'}, {0x7F070004: '-1033'}, {2131165190: '32448'}]},
                                     {36707: [{2131165187: '-6305'}, {0x7F070004: '-1036'}, {2131165190: '45181'}]}
                                     ],
                      'test_nr_registration': [{21: [{2131165187: '-6297'}, {0x7F070004: '-1035'}, {2131165190: '32566'}]},
                                       {13621: [{2131165187: '-6291'}, {0x7F070004: '-1036'}, {2131165190: '39479'}]},
                                       {26612: [{2131165187: '-6312'}, {0x7F070004: '-1037'}, {2131165190: '32286'}]}
                                       ]
                      }

    # 指定采样点信令
    signal_res_dict = {
        'test_call': {
            4413: {'0xFFF1E207': 'IMS_SIP_INVITE->Ringing'},
            7022: {'0xfff20000': 'NR DCI Information'},
            8736: {'0xfff1e208': 'NR PDCP DLRbs Stats'},
            7044: {'0xfff1e207': 'NR MAC UL Physical Channel Schedule Report'}
        },
        'test_ftpdown': {
            30: {'0xfff1e209': 'NR MAC UL Physical Channel Schedule Report'},
            60: {'0xd1001c07': 'NR CSF Information'},
            1361: {'0xfff1e005': 'NR PDCP DLRbs Stats'},
            14129: {'0xfff1e209': 'NR DCI Information'}
        },
        'test_iperf': {
            18: {'0xfff1e215': 'NR CSF Information'},
            234: {'0xfff1e207': 'NR MAC UL Physical Channel'},
            1221: {'0xfff1e00c': 'NRCSF Information'},
            14909: {'0xfff1e207': 'NR MAC UL Physical Channel Schedule Report'}
        },
        'test_ping': {
            4222: {'0xfff1e207': 'NR MAC UL Physical Channel Schedule Report'},
            10752: {'0xfff1e200': 'IMS_SIP_SUBSCRIBE'},
            287: {'0xfff1e205': 'NR DCI Information'}
        },
        'test_nr_registration': {
           182: {'0xfff1e20a': 'NR PDCP DL Rbs Stats'},
           2236: {'0xfff1e205': 'NR MAC UL Physical Channel Schedule Report'},
           5396: {'0xfff1e205': 'NR PDCP UL Stats'},
           13785: {'0xfff1e205': 'IMS_SIP_REGISTER->OK'}
        },
        'test_ftpup': {
           111: {'0xfff1e208': 'NR PDCP UL Stats'},
           2121: {'0xfff20000': 'NR DCI Information'},
           12224: {'0xfff1e205': 'NR PDCP DL Rbs Stats'}
        },
        'test_lteattach': {
            91: {'0xd1007001': 'IMS_SIP_REGISTER->OK'},
            232: {'0x50000201': 'IMS_SIP_NOTIFY'},
            3911: {'0xfff1e208': 'NR->ULInformationTransfer'},
            3595: {'0xfff1e00c': 'NR CSF Information'},
        }
                      }

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
        with allure.step('正常清理所有服务'):
            print('正常清理所有服务', exe_path)
            start_service(exe_path, config_xml_path)
            print('数据集测试结束，正常清理所有服务，等待 20s ......')
        time.sleep(10)

    @allure.step("DCSDataSets数据集回归测试Call业务")
    def test_call(self):
        file = 'test_call.qmdl'
        self.run_all_step(file)

    @allure.step("DCSDataSets数据集回归测试Ping业务")
    def test_ping(self):
        file = 'test_ping.qmdl'
        self.run_all_step(file)

    @allure.step("DCSDataSets数据集回归测试Iperf业务")
    def test_iperf(self):
        file = 'test_iperf.qmdl'
        self.run_all_step(file)

    @allure.step("DCSDataSets数据集回归测试Ftpdownload业务")
    def test_ftpdownload(self):
        file = 'test_ftpdown.qmdl'
        self.run_all_step(file)

    @allure.step("DCSDataSets数据集回归测试Ftpupload业务")
    def test_ftpupload(self):
        file = 'test_ftpup.qmdl'
        self.run_all_step(file)

    @allure.step("DCSDataSets数据集回归测试Attach业务")
    def test_attach(self):
        file = 'test_lteattach.qmdl'
        self.run_all_step(file)

    @allure.step("DCSDataSets数据集回归测试Registration业务")
    def test_nr_registration(self):
        file = 'test_nr_registration.qmdl'
        self.run_all_step(file)

    def run_all_step(self, file):
        with allure.step('当前推送的文件为：{0}'.format(file)):
            print('当前推送的文件为：{0}'.format(file))
            with allure.step('发送 start work 命令'):
                print('发送 start work 命令,并等待所有通道准备好')
                time.sleep(20)
                self.send_start_work_cmd()

            with allure.step('推送原始数据给数据集，推送文件为：{0}'.format(file)):
                print('推送原始数据给数据集, 推送文件为：{0}'.format(file))
                self.read_qmdl_and_send_to_DCSDataSets(os.path.join(TestDCSDataSets.data_path, file))
                time.sleep(3)
            #
            with allure.step('获取总采样点'):
                self.get_cur_point_count_from_redis(file.split('.')[0])
                time.sleep(2)
            #
            with allure.step('发送命令给数据集服务，获取事件相关信息'):
                self.get_res_data_from_DCSDataSets(TestDCSDataSets.event_code_dict, file.split('.')[0],
                                                   TestDCSDataSets.event_dict[file.split('.')[0]])
                time.sleep(2)
            #
            with allure.step('获取信令, 并对获取的信令信息进行核对'):
                self.get_msg_code_info(TestDCSDataSets.signal_res_dict[file.split('.')[0]])
                time.sleep(2)
            #
            with allure.step('发送命令给数据集服务，查询常用指定参数值'):
                self.query_comparison_param_value_new(TestDCSDataSets.param_res_dict[file.split('.')[0]])
                time.sleep(2)
            #
            with allure.step('发送 stop work 命令'):
                print('发送 stop work 命令')
                self.send_stop_work_cmd()
                print('当前用例所有任务已结束，等待10秒进入下一个用例')
                time.sleep(10)

    def send_start_work_cmd(self):
        ddib_path = os.path.join(local_tmp_path, 'DCSDataSets_auto_test')
        if os.path.exists(ddib_path + '.ddib'):
            os.remove(ddib_path + '.ddib')
        cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                    'method': 'start_work',
                    'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiAutoTest',
                    'test_port': 4,
                    'file_name': os.path.join(local_tmp_path, 'DCSDataSets_auto_test')
                    }
        pub_json_cmd_to_redis_chanel(TestDCSDataSets.package_project, cmd_json, pubsub, TestDCSDataSets.redis_chanel)

    def send_stop_work_cmd(self):
        for i, v in enumerate(test_port_list):
            port = test_port_list[i]
            cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                        'method': 'stop_work',
                        'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSTestMgr-10',
                        'test_port': port}

            pub_json_cmd_to_redis_chanel(TestDCSDataSets.package_project, cmd_json, pubsub,
                                         TestDCSDataSets.redis_chanel)
        time.sleep(10)

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

    # 获取指定的事件列表 && 事件统计
    def deal_event_res_data(self, event_code_dict, event_data, file_name):
        print('params: ', event_data['params'])
        event_count = {}
        event_list = []
        for params_content in event_data['params']:
            event_flag = params_content['event_flag']
            if event_flag not in event_list:
                # 获取采样点期间事件列表
                event_list.append(hex(event_flag))
            else:
                pass
            if hex(event_flag) in event_list:
                if hex(event_flag) not in event_count.keys():
                    event_count[hex(event_flag)] = 1
                else:
                    event_count[hex(event_flag)] = event_count[hex(event_flag)] + 1
        return event_count, event_list

    def get_cur_point_count_from_redis(self, file_name):
        total_point_dict = {'test_call': 12502, 'test_ping': 24746, 'test_iperf': 18303, 'test_lteattach': 37193,
                            'test_ftpdown': 14340, 'test_ftpup': 22649, 'test_nr_registration': 27123}
        for i, v in enumerate(test_port_list):
            port = int(test_port_list[i])
            cmd_json_mould = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                              'method': 'get_total_point_count',
                              'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSTestMgr-10',
                              'test_port': port
                              }
            cur_point_count = pub_json_cmd_to_redis_chanel(TestDCSDataSets.package_project, cmd_json_mould, pubsub,
                                                           TestDCSDataSets.redis_chanel)['total_point_count']
            with check.check:
                with allure.step('当前测试端口为{0}：'.format(port)):
                    print('当前测试端口为{0}：'.format(port))
                    with allure.step('获取出的实际总采样点个数为：{0}，期望值为：{1}'.format(cur_point_count, total_point_dict[file_name])):
                        print('获取出的实际总采样点个数为：{0}，期望值为：{1}'.format(cur_point_count, total_point_dict[file_name]))
                        assert cur_point_count == total_point_dict[file_name]

    # 从数据集获取事件信息、并分析汇总
    def get_res_data_from_DCSDataSets(self, event_code_dict, file_name, event_dict):
        event_count_all = []
        new_event_count_all = []
        for i, v in enumerate(test_port_list):
            port = int(test_port_list[i])
            cmd_json_mould = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                              'method': 'get_total_point_count',
                              'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSTestMgr-10',
                              'test_port': port}
            cur_point_count = pub_json_cmd_to_redis_chanel(TestDCSDataSets.package_project, cmd_json_mould, pubsub,
                                                    TestDCSDataSets.redis_chanel)['total_point_count']

            point_list = self.split_number(cur_point_count)

            with allure.step('当前测试端口为：{0}'.format(port)):
                print('当前测试端口为：{0}'.format(port))
                # 查询事件
                with allure.step('发送查询事件命令给数据集'):
                    cmd_json_mould['method'] = 'get_multi_event_info'
                    for point_range in point_list:
                        with allure.step(
                                '当前查询的起始采样点为：{0}，结束采样点为{1}'.format(point_range[0], point_range[1])):
                            cmd_json_mould['start_point_index'] = point_range[0]
                            cmd_json_mould['end_point_index'] = point_range[1]

                            event_data = pub_json_cmd_to_redis_chanel(TestDCSDataSets.package_project, cmd_json_mould,
                                                                      pubsub, TestDCSDataSets.redis_chanel)

                            event_count, event_list = self.deal_event_res_data(event_code_dict, event_data, file_name)
                            if event_count:
                                if event_count not in event_count_all:
                                    event_count_all.append(event_count)
                            with allure.step('查询当前采样点期间获取事件及事件次数为：{0}'.format(event_count_all)):
                                print('查询当前采样点期间获取事件及事件次数为：{0}'.format(event_count_all))

                        # 按照事件键值进行合并，将相同键的值相加，并将结果保存在列表
                        for dict_item in event_count_all:
                            if dict_item:  # 检查字典是否为空
                                for key, value in dict_item.items():
                                    found = False
                                    for i, item in enumerate(new_event_count_all):
                                        if key in item:
                                            new_event_count_all[i][key] += value
                                            found = True
                                            break
                                    if not found:
                                        new_event_count_all.append({key: value})
                        print('new_event_count_all', new_event_count_all)
                with allure.step('分析事件结果，所有采样点查询返回的结果为{0}：'.format(new_event_count_all)):
                    print('分析事件结果，所有采样点查询返回的结果为{0}：'.format(new_event_count_all))

                with allure.step('发送查询事件命令给数据集, 获取指定采样点的事件码evnet_code及event_index'):
                    for point_index in event_dict.keys():
                        cmd_json_mould['start_point_index'] = point_index - 100
                        cmd_json_mould['end_point_index'] = point_index + 100

                        event_data = pub_json_cmd_to_redis_chanel(TestDCSDataSets.package_project,
                                                                  cmd_json_mould, pubsub, TestDCSDataSets.redis_chanel)
                        # 从字典中拿出期望事件码event_code及 event_index
                        event_code = event_dict.get(point_index, {}).get('event_code')
                        event_index_dict = event_dict.get(point_index, {}).get('event_index')

                        for point_index1 in event_data['params']:
                            res_point_index = point_index1['point_index']
                            res_event_code = hex(point_index1['event_flag'])
                            res_event_index = point_index1['event_index']
                            if int(res_event_code, 16) == int(event_code, 16) and res_event_index == event_index_dict \
                                    and res_point_index == point_index:
                                with check.check:
                                    with allure.step('实际采样点为：{0},获取实际事件码为：{1},实际事件index为：{2},'
                                                     '期望采样点为：{3}, 期望事件码：{4}, 期望事件index:{5},符合预期'
                                                             .format(point_index, res_event_code, res_event_index,
                                                                     point_index, event_code, event_index_dict)):
                                        print('实际采样点为：{0},获取实际事件码为：{1},实际事件index为：{2},'
                                                     '期望采样点为：{3}, 期望事件码：{4}, 期望事件index:{5}'
                                              .format(res_point_index, res_event_code, res_event_index,
                                                      point_index, event_code, event_index_dict))
                                        assert int(res_event_code, 16) == int(event_code, 16) and \
                                               res_event_index == event_index_dict and res_point_index == point_index

    def get_msg_code_info(self, msg_code_all):
        for i, v in enumerate(test_port_list):
            port = int(test_port_list[i])
            with allure.step('当前测试端口为：{0}'.format(port)):
                for point_index in msg_code_all.keys():
                    with allure.step('当前采样点是：{0}'.format(point_index)):
                        cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                                    'method': 'get_msg_code_info',
                                    'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                                    'test_port': port,
                                    'point_index': point_index,
                                    'is_utc_time': 0,
                                    'is_handset_time': 0}

                        cmd_res = pub_json_cmd_to_redis_chanel(TestDCSDataSets.package_project, cmd_json, pubsub,
                                                               TestDCSDataSets.redis_chanel)
                        # 通过命令获取实际信令码
                        res_msg_code_info = cmd_res['msg_code']
                        # 提取期望信令码
                        keys = list(msg_code_all[point_index].keys())[0]
                        # 提取信令名称,用next 函数取出期望值信令码
                        msg_code_name = next(iter(msg_code_all[point_index].values()))
                        with check.check:
                            with allure.step('对信令信息进行核对，获取出的信令码为：{0},期望信令码为：{1}, 期望信令名称为：{2}'.
                                                     format(hex(res_msg_code_info), keys, msg_code_name)):
                                print('对信令信息进行核对，获取出的信令码为：{0},期望信令码为：{1}, 期望信令名称为：{2}'.
                                                     format(hex(res_msg_code_info), keys, msg_code_name))
                                assert res_msg_code_info == int(keys, 16)

    # 查询&对比参数
    def query_comparison_param_value_new(self, param_res_dict):
        param_swap_dict = {2131165187: 'NR-RSRP', 0x7F070004: 'NR-RSRQ', 2131165190: 'NR-SINR'}
        # 使用列表推导式提取键到一个列表
        point_index_list = [list(d.keys())[0] for d in param_res_dict]
        # 查询参数
        for i, v in enumerate(test_port_list):
            port = int(test_port_list[i])
            with allure.step('当前测试端口是：{0}'.format(port)):
                for point_index in point_index_list:
                    with allure.step('当前采样点是：{0}'.format(point_index)):
                        for param_code in list(param_swap_dict.keys()):
                            cmd_json_mould = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                                              'method': 'get_param_int64_value',
                                              'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSTestMgr-10',
                                              'test_port': port,
                                              'filter': 0,
                                              'param_key': param_code,
                                              'point_index': point_index
                                              }
                            param_data = pub_json_cmd_to_redis_chanel(TestDCSDataSets.package_project, cmd_json_mould,
                                                                      pubsub, TestDCSDataSets.redis_chanel)
                            # 提取实际的参数值
                            res_param_value = param_data['param_value']
                            # 取出实际值匹配数据集工具除100后取整
                            new_res_param_value1 = round(res_param_value / 100)
                            # 取出实际值匹配数据集工具除100后保留2位小数
                            new_res_param_value2 = round(res_param_value / 100, 2)

                            # 使用嵌套循环和键的索引、next函数获取迭代对象操作逐一提取内层值
                            for d in param_res_dict:
                                if point_index in d:
                                    inner_list = d[point_index]
                                    # next() 函数用于获取迭代器的下一个元素
                                    inner_dict = next((inner_dict for inner_dict in inner_list if param_code in inner_dict), None)
                                    if inner_dict:
                                        # 提取期望参数值
                                        param_value = int(inner_dict[param_code])
                                        # 取出期望值匹配数据集工具除100后取整
                                        new_param_value1 = round(param_value / 100)
                                        # 取出期望值匹配数据集工具四舍五入保留2位小数
                                        new_param_value2 = round(param_value / 100, 2)
                                        # 提取参数名称
                                        param_name = param_swap_dict[param_code]

                                        # 期望参数值与实际取出参数值进行对比断言：
                                        with check.check:
                                            with allure.step('当前查询参数code：{0}，参数对应名称为：{1}'
                                                                     .format(param_code, param_name)):
                                                with allure.step('四舍五入取整后的结果：期望值为：{0}，实际值为：{1},'
                                                                 .format( new_param_value1, new_res_param_value1)):
                                                    print('期望值为：{0}，取出的值为：{1},'
                                                                 .format(new_param_value1, new_res_param_value1))
                                                    assert new_res_param_value1 == new_param_value1

                                                with allure.step('实际取出的结果期望值为：{0}，取出的值为：{1},'
                                                                 .format( param_value, res_param_value)):
                                                    print('期望值为：{0}，取出的值为：{1},'
                                                                 .format(param_value, res_param_value))
                                                    assert res_param_value == param_value

                                                with allure.step('四舍五入保留2位小数后的结果:期望值为：{0}，实际值为：{1},'
                                                                 .format(new_param_value2, new_res_param_value2)):
                                                    print('结果四舍五入保留2位小数后的结果:期望值为：{0}，取出的值为：{1},'
                                                                 .format(new_param_value2, new_res_param_value2))
                                                    assert new_res_param_value2 == new_param_value2

    def split_number(self, num):
        result = []
        for i in range(0, num, 4500):
            result.append((i, i + 4499 if i + 4499 < num else num))
        return result


if __name__ == "__main__":
    new_test = TestDCSDataSets()
    new_test.setup_class()
    # 推送数据
    new_test.test_call()
    new_test.test_ping()
    new_test.test_iperf()
    new_test.test_ftpdownload()
    new_test.test_ftpupload()
    new_test.test_attach()
    new_test.test_nr_registration()

    print('清理所有服务')
    os.system(r'D:\DCS\bin\killservices.bat')

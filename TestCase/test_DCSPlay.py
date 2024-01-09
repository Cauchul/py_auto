# -*- coding:utf-8 -*-
import json
import struct
import time

import allure
import pytest
from pytest_check import check

from Common.GobalVariabies import *


# 1 发命令给精灵服务，拉起回放服务
def start_dcs_play_get_test_port():
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'start',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'server_name': 'DCSPlay',
                'test_port': -1,
                'file_path': TestDCSPlay.dcs_play_file}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_daemon_chanel)
    print('cmd_res: ', cmd_res)
    res_test_port = cmd_res['test_port']
    print('res_test_port: ', res_test_port)
    return res_test_port


# 2 发送回放命令
def send_file_play_cmd():
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'file_play',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port,
                'file_name': TestDCSPlay.dcs_play_file}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    print(cmd_res)
    if 0 != cmd_res['status']:
        pytest.exit('发送 file_play 命令给 DCSPlay 服务，返回状态错误', returncode=1)


# 3 获取总采样点
def get_total_point_count():
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_total_point_count',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    point = cmd_res['total_point_count']
    return point


# 4 获取采样点的信令码
def get_msg_code(point):
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_msg_code',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'point_index': point}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub,
                                           TestDCSPlay.dcs_play_chanel)
    res_msg_code = cmd_res['msg_code']
    return res_msg_code


# 5 从指定采样点开始，获取信令码的采样点
def get_next_msg_code_index(code=4294042115, point=0):
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_next_msg_code_index',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'point_index': point, 'msg_code': code, 'is_down': 1}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_next_point_index = cmd_res['point_index']
    return res_next_point_index


# 6 获取采样点的时间
def get_point_index_time(point):
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_point_index_time',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'point_index': point, 'is_utc_time': 0, 'is_handset_time': 0}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_point_time = cmd_res['time']
    return res_point_time


# 7 获取信令码上行还是下行
def get_msg_code_direction(point):
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_msg_code_direction',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'point_index': point}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_msg_code_direction = cmd_res['direction']
    return res_msg_code_direction


# 8
def get_layer3_original_msg_content(point=0):
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_layer3_original_msg_content',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'point_index': point}

    json_cmd_res, raw_data_res = pub_json_cmd_to_redis_chanel_get_raw(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    return raw_data_res


# 9
def get_msg_detail_content(point=1):
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_msg_detail_content',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'point_index': point}

    json_cmd_res, raw_data_res = pub_json_cmd_to_redis_chanel_get_raw(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    return raw_data_res


# 10 获取当前采样点的信令码信息
def get_msg_code_info(point):
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_msg_code_info',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'point_index': point, 'is_utc_time': 0, 'is_handset_time': 0}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_msg_code_info = {'direction': cmd_res['direction'], 'time': cmd_res['time']}
    return res_msg_code_info


# 11 获取采样点指定参数的参数值，返回类型为double类型
def get_param_double_value(point):
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_param_double_value',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'point_index': point, 'param_key': 2131165187, 'filter': 1}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_param_double_value = cmd_res['param_value']
    return res_param_double_value


# 12 获取采样点指定参数的参数值，返回值为int64类型
def get_param_int64_value(point):
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_param_int64_value',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'point_index': point, 'param_key': 2131165187, 'filter': 1}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_param_int64_value = cmd_res['param_value']
    return res_param_int64_value


# 13 获取指定参数值的真实值数量
def get_param_real_value_total_count():
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_param_real_value_total_count',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'param_key': 2131165187}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_real_value_total_count = cmd_res['total_point_count']
    return res_real_value_total_count


# 14 获取指定第一个真实值的采样点
def get_point_index_by_param_real_value_index():
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_point_index_by_param_real_value_index',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'param_key': 2131165187, 'param_index': 1}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_real_value_index = cmd_res['point_index']
    return res_real_value_index


# 15 获取当前采样点是第几个真实值
def get_param_real_value_index_by_point_index(point):
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_param_real_value_index_by_point_index',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'param_key': 2131165187, 'point_index': point}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_param_real_value_index = cmd_res['param_index']
    return res_param_real_value_index


# 16 获取结构体小区个数
def get_struct_item_count(point=13):
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_struct_item_count',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'point_index': point, 'filter': 1, 'serviceid': 0xE002}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_struct_item_count = cmd_res['count']
    return res_struct_item_count


# 17 获取结构体小区信息
def get_struct_item(point):
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_struct_item',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'point_index': point, 'filter': 0, 'serviceid': 0xE002, 'item_index': 0}

    json_cmd_res, raw_data_res = pub_json_cmd_to_redis_chanel_get_raw(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    return raw_data_res


# 18 获取结构体子小区的个数
def get_struct_sub_item_count(point):
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_struct_sub_item_count',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'point_index': point, 'filter': 1, 'serviceid': 0xE002, 'item_index': 0}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_sub_item_count = cmd_res['count']
    return res_sub_item_count


# 19 获取结构体子小区的个数
def get_struct_sub_item(point):
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_struct_sub_item',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'point_index': point, 'filter': 1, 'serviceid': 0xE002, 'item_index': 0, 'subitem_index': 0}

    json_cmd_res, raw_data_res = pub_json_cmd_to_redis_chanel_get_raw(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    return raw_data_res


# 20  获取多个子小区
def get_struct_multi_sub_item_count():
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_struct_multi_sub_item_count',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'point_index': 13, 'filter': 1, 'serviceid': 0xE002, 'item_index': 0, 'subitem_index': 0}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_multi_sub_item_count = cmd_res['count']
    return res_multi_sub_item_count


# 21 获取多重子小区的信息
def get_struct_multi_sub_item():
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_struct_multi_sub_item',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'point_index': 13, 'filter': 1, 'serviceid': 1,
                'item_index': 1, 'subitem_index': 1, 'multi_subitem_index': 1}

    json_cmd_res, raw_data_res = pub_json_cmd_to_redis_chanel_get_raw(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    return raw_data_res


# 22 获取多条信令码信息
def get_multi_msg_code_info():
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_multi_msg_code_info',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'start_point_index': 13, 'end_point_index': 15}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_multi_msg_code_info = cmd_res['params']
    return res_multi_msg_code_info


# 23 获取多条参数信息
def get_multi_param_info():
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_multi_param_info',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'start_point_index': 13, 'end_point_index': 28,
                'params': [2131165187, 2131165188, 2131165190]}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_multi_param_info = cmd_res['params']
    return res_multi_param_info


# 24  获取多个采样点的事件信息
def get_multi_event_info():
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_multi_event_info',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'start_point_index': 13, 'end_point_index': 28}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_multi_event_info = cmd_res['params']
    return res_multi_event_info


# 25  获取事件详细信息
def get_event_detail_msg():
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_event_detail_msg',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'event_flag': 1, 'event_index': 13}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_event_detail_msg = cmd_res
    return res_event_detail_msg


# 26 LTE网络
def get_set_cell_count_by_set_type():
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_set_cell_count_by_set_type',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'net_type': 7, 'set_type': 13, 'point_index': 13, 'is_evdo': 0, 'filter': 1}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_set_cell_count = cmd_res
    return res_set_cell_count


# 27 LTE网络
def get_set_cell_param_value_by_set_type():
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_set_cell_param_value_by_set_type',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'net_type': 7, 'set_type': 13, 'point_index': 13,
                'item_index': 0, 'cell_param_key': 2131165187, 'is_evdo': 0, 'filter': 1}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_set_cell_param_value = cmd_res
    return res_set_cell_param_value


# 28  返回信令码的所有采样点
def get_msg_code_point_index_list(point):
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_msg_code_point_index_list',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'msg_code': 0xFFF1E003, 'start_point_index': 0, 'end_point_index': point}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    return {'count': cmd_res['count'], 'params': cmd_res['params']}


# 29 # 获取存在的信令码的类型 层一层二还是层三信令
def get_exist_msg_code_type_list():
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_exist_msg_code_type_list',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_type_list = cmd_res['params']
    return res_type_list


# 30 获取事件标记列表
def get_exist_event_flag_list():
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_exist_event_flag_list',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_event_flag_list = cmd_res['params']
    return res_event_flag_list


# 31  获取事件属性列表
def get_event_property_list():
    cmd_json = {'from': 'PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest',
                'method': 'get_event_property_list',
                'reqid': '1681114024453762PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.ZhuhaiDCSautotest',
                'test_port': TestDCSPlay.dcs_play_test_port, 'event_flag': 0xE02, 'event_index': 0,
                'params': [2131165187, 2131165188, 2131165190]}

    cmd_res = pub_json_cmd_to_redis_chanel(TestDCSPlay.package_project, cmd_json, pubsub, TestDCSPlay.dcs_play_chanel)
    res_event_property_list = cmd_res['params']
    return res_event_property_list


check_list = [0, 13, 14, 27]
msg_code_std_dict = {13: 4294042133, 14: 4294042121, 27: 4294042133, 0: 4294049792, 18616: 4294042119}
next_point_index_std_dict = {13: 1415, 14: 1415, 27: 1415, 0: 1415, 18616: -9999}
point_time_std_dict = {13: 317794071666000, 14: 317794071689000, 27: 317794071986000, 0: 317794071346000, 18616: 317794398153000}
msg_code_direction_std_dict = {13: 2, 14: 2, 27: 2, 0: 2, 18616: 2}
msg_code_info_std_info = {13: {'direction': 2, 'time': 317794071666000}, 14: {'direction': 2, 'time': 317794071689000},
                          27: {'direction': 2, 'time': 317794071986000}, 0: {'direction': 2, 'time': 317794071346000},
                          18616: {'direction': 2, 'time': 317794398153000}}
param_double_value_std_info = {13: -71.67, 14: -9999.0, 27: -71.42, 0: -9999.0, 18616: -9999.0}
param_int64_value_std_info = {13: -7167, 14: -9999, 27: -7142, 0: -9999, 18616: -9999}
param_real_value_index_std_info = {13: 0, 14: 0, 27: 1, 0: -9999, 18616: 1019}
struct_item_count_std_info = {13: 1, 14: 0, 27: 1, 0: 0, 18616: 0}
struct_item_std_info = {13: (0, 0, 627264, 20), 14: (0, 0, 627264, 20), 27: (0, 0, 627264, 20), 0: (),
                        18616: (0, 0, 627264, 20)}
struct_sub_item_count_std_info = {13: 1, 14: 0, 27: 1, 0: 0, 18616: 0}
struct_sub_item_std_info = {13: (0, True, 0, -1671178794, -71.66666412353516, -10.359375, 33.22726058959961),
                            27: (0, True, 0, -1671178794, -71.421875, -10.359375, 32.413856506347656)}


def out_std_info():
    print('msg_code_std_dict：', msg_code_std_dict)
    print(next_point_index_std_dict)
    print(point_time_std_dict)
    print(msg_code_direction_std_dict)
    print(msg_code_info_std_info)
    print(param_double_value_std_info)
    print(param_int64_value_std_info)
    print(param_real_value_index_std_info)
    print(struct_item_count_std_info)
    print(struct_item_std_info)
    print(struct_sub_item_count_std_info)
    print(struct_sub_item_std_info)


def generate_std_info(point_list):
    for point in point_list:
        msg_code = get_msg_code(point)
        print('check_msg_code: ', msg_code)
        msg_code_std_dict[point] = msg_code

        next_point_index = get_next_msg_code_index(point=point)
        print('next_point_index: ', next_point_index)
        next_point_index_std_dict[point] = next_point_index

        point_time = get_point_index_time(point)
        print('point_time: ', point_time)
        point_time_std_dict[point] = point_time

        msg_code_direction = get_msg_code_direction(point)
        print('msg_code_direction: ', msg_code_direction)
        msg_code_direction_std_dict[point] = msg_code_direction

        msg_code_info = get_msg_code_info(point)
        print('msg_code_info: ', msg_code_info)
        msg_code_info_std_info[point] = msg_code_info

        param_double_value = get_param_double_value(point)
        print('param_double_value: ', param_double_value)
        param_double_value_std_info[point] = param_double_value

        param_int64_value = get_param_int64_value(point)
        print('param_int64_value: ', param_int64_value)
        param_int64_value_std_info[point] = param_int64_value

        param_real_value_index = get_param_real_value_index_by_point_index(point)
        print('param_real_value_index: ', param_real_value_index)
        param_real_value_index_std_info[point] = param_real_value_index

        struct_item_count = get_struct_item_count(point)
        print('struct_item_count: ', struct_item_count)
        struct_item_count_std_info[point] = struct_item_count

        struct_raw_data = get_struct_item(point)
        print('struct_raw_data: ', struct_raw_data)
        num_elements = len(struct_raw_data) // 4
        unpack_struct_data = struct.unpack('<' + 'I' * num_elements, struct_raw_data)
        print('unpack_struct_data: ', unpack_struct_data)
        struct_item_std_info[point] = unpack_struct_data

        sub_item_count = get_struct_sub_item_count(point)
        print('sub_item_count: ', sub_item_count)
        struct_sub_item_count_std_info[point] = sub_item_count

        sub_item_raw_data = get_struct_sub_item(point)
        print('sub_item_raw_data: ', sub_item_raw_data)
        if sub_item_raw_data:
            sub_item_data = struct.unpack('<i?iifff', sub_item_raw_data)
            print('sub_item_data: ', sub_item_data)
            struct_sub_item_std_info[point] = sub_item_data


def datasets_interface_call_data_check(point_index):
    msg_code = get_msg_code(point_index)
    with allure.step('检查msg_code'):
        with allure.step('期望值：{0}，实际值：{1}'.format(msg_code_std_dict[point_index], msg_code)):
            assert msg_code_std_dict[point_index] == msg_code

    next_point_index = get_next_msg_code_index(point=point_index)
    with allure.step('检查msg_code 4294042115的下一个采样点的index'):
        with allure.step('期望值：{0}，实际值：{1}'.format(next_point_index_std_dict[point_index], next_point_index)):
            assert next_point_index_std_dict[point_index] == next_point_index

    point_time = get_point_index_time(point_index)
    with allure.step('检查采样点时间'):
        with allure.step('期望值：{0}，实际值：{1}'.format(point_time_std_dict[point_index], point_time)):
            assert point_time_std_dict[point_index] == point_time

    msg_code_direction = get_msg_code_direction(point_index)
    with allure.step('检查信令方向为'):
        with allure.step('期望值：{0}，实际值：{1}'.format(msg_code_direction_std_dict[point_index], msg_code_direction)):
            assert msg_code_direction_std_dict[point_index] == msg_code_direction

    msg_code_info = get_msg_code_info(point_index)
    with allure.step('检查信令信息'):
        with allure.step('期望值：{0}，实际值：{1}'.format(msg_code_info_std_info[point_index], msg_code_info)):
            assert msg_code_info_std_info[point_index] == msg_code_info

    param_double_value = get_param_double_value(point_index)
    with allure.step('检查RSRP的double类型值'):
        with allure.step('期望值：{0}，实际值：{0}'.format(param_double_value_std_info[point_index], param_double_value)):
            assert param_double_value_std_info[point_index] == param_double_value

    param_int64_value = get_param_int64_value(point_index)
    with allure.step('检查RSRP的int64类型值}'):
        with allure.step('期望值：{0}，实际值：{0}'.format(param_int64_value_std_info[point_index], param_int64_value)):
            assert param_int64_value_std_info[point_index] == param_int64_value

    real_value_total_count = get_param_real_value_total_count()
    with allure.step('检查RSRP的真实值总量'):
        with allure.step('期望值：1020，实际值：{0}'.format(real_value_total_count)):
            assert 1020 == real_value_total_count

    real_real_value_point_index = get_point_index_by_param_real_value_index()
    with allure.step('检查RSRP第一个真实值的采样点'):
        with allure.step('期望值：27，实际值：{0}'.format(real_real_value_point_index)):
            assert 27 == real_real_value_point_index

    param_real_value_index = get_param_real_value_index_by_point_index(point_index)
    with allure.step('检查采样点是RSRP的第几个真实值'):
        with allure.step('期望值：{0}，实际值：{1}'.format(param_real_value_index_std_info[point_index], param_real_value_index)):
            assert param_real_value_index_std_info[point_index] == param_real_value_index

    struct_item_count = get_struct_item_count(point_index)
    with allure.step('检查结构体小区个数'):
        with allure.step('期望值：{0}，实际值：{1}'.format(struct_item_count_std_info[point_index], struct_item_count)):
            assert struct_item_count_std_info[point_index] == struct_item_count

    struct_raw_data = get_struct_item(point_index)
    num_elements = len(struct_raw_data) // 4
    unpack_struct_data = struct.unpack('<' + 'I' * num_elements, struct_raw_data)
    with allure.step('检查采样点，serviceid为0xE002的结构体小区信息'):
        with allure.step('期望值：{0}，实际值：{1}'.format(struct_item_std_info[point_index], unpack_struct_data)):
            assert struct_item_std_info[point_index] == unpack_struct_data

    sub_item_count = get_struct_sub_item_count(point_index)
    with allure.step('检查采样点 ，serviceid为0xE002的结构体子小区数量'):
        with allure.step('期望值：{0}，实际值：{1}'.format(struct_sub_item_count_std_info[point_index], sub_item_count)):
            assert struct_sub_item_count_std_info[point_index] == sub_item_count

    sub_item_raw_data = get_struct_sub_item(point_index)
    if sub_item_raw_data:
        sub_item_data = struct.unpack('<i?iifff', sub_item_raw_data)
        with allure.step('检查采样点，serviceid为0xE002的结构体子小区信息'):
            with allure.step('期望值：{0}，实际值：{1}'.format(struct_sub_item_std_info[point_index], sub_item_data)):
                assert struct_sub_item_std_info[point_index] == sub_item_data

    multi_msg_code_info = get_multi_msg_code_info()
    msg_code_standard_info = [{'direction': 2, 'handset_time': 317794071666000, 'msg_code': 4294042133,
                               'pc_time': 317794071666000, 'point_index': 13},
                              {'direction': 2, 'handset_time': 317794071689000, 'msg_code': 4294042121,
                               'pc_time': 317794071689000, 'point_index': 14}]
    with allure.step('检查采样点 13~15 的msg_code信息'):
        with allure.step('期望值：{0}，实际值：{1}'.format(msg_code_standard_info, multi_msg_code_info)):
            assert msg_code_standard_info == multi_msg_code_info

    multi_param_info = get_multi_param_info()
    param_standard_info = [{'2131165187': [[13, -7167], [27, -7142]]},
                           {'2131165188': [[13, -1036], [27, -1036]]},
                           {'2131165190': [[13, 33227], [27, 32414]]}]
    with allure.step('检查采样点 13~28 的RSRP、RSRQ、SINR值'):
        with allure.step('期望值：{0}，实际值：{1}'.format(param_standard_info, multi_param_info)):
            assert param_standard_info == multi_param_info

    print('TestDCSPlay.total_point: ', TestDCSPlay.total_point)
    point_index_data = get_msg_code_point_index_list(TestDCSPlay.total_point)
    standard_index_data = {'count': 7, 'params': [5027, 6997, 9250, 10537, 13363, 13611, 13775]}
    with allure.step('检查参数code 0xFFF1E003 的出现次数和对应采样点'):
        with allure.step('期望值：{0}，实际值：{1}'.format(standard_index_data, point_index_data)):
            assert standard_index_data == point_index_data

    type_list = get_exist_msg_code_type_list()
    with allure.step('检查信令类型'):
        check_flag = False
        if all(item in type_list for item in [0xFFF1E01B, 0xFFF1E215, 0xFFF1E003, 0xD1001C07, 0xFFF1E207]):
            check_flag = True
        with allure.step('信令类型0xFFF1E01B,0xFFF1E215,0xFFF1E003,0xD1001C07，'
                         '0xFFF1E207是否能在所有的信令类型中找到，期望值：True，实际值：{0}'.format(check_flag)):
            assert check_flag

    msg_detail_content = get_msg_detail_content(point_index)
    with allure.step('采样点的信令详情为：{0}'.format(msg_detail_content)):
        # print('msg_detail_content: ', msg_detail_content)
        pass

    msg_content = get_layer3_original_msg_content()
    print('msg_content: ', msg_content)

    multi_event_info = get_multi_event_info()
    print('multi_event_info: ', multi_event_info)

    event_flag_list = get_exist_event_flag_list()
    print('event_flag_list: ', event_flag_list)

    event_property_list = get_event_property_list()
    print('event_property_list: ', event_property_list)

    # UI那边在暂时还未用到
    # multi_sub_item_count = get_struct_multi_sub_item_count()
    # print('multi_sub_item_count: ', multi_sub_item_count)

    # UI那边在暂时还未用到
    # multi_sub_item = get_struct_multi_sub_item()
    # print('multi_sub_item: ', multi_sub_item)

    # UI那边在暂时还未用到
    # event_detail_msg = get_event_detail_msg()
    # print('event_detail_msg: ', event_detail_msg)

    #  LTE 网络数据使用
    # res_set_cell_count = get_set_cell_count_by_set_type()
    # print('res_set_cell_count: ', res_set_cell_count)

    # set_cell_param_value = get_set_cell_param_value_by_set_type()
    # print('set_cell_param_value: ', set_cell_param_value)


def datasets_interface_call_forward_replay(point_index):
    # 获取采样点的 msg_code
    msg_code = get_msg_code(point_index)
    with allure.step('msg_code为：{0}'.format(msg_code)):
        assert msg_code

    # 获取msg_code的下一个采样点
    next_point_index = get_next_msg_code_index(point=point_index)
    with allure.step('正向获取msg_code 4294042115的下一个采样点的index为：期望值：值不为空，实际值：{0}'.format(next_point_index)):
        assert next_point_index

    point_time = get_point_index_time(point_index)
    with allure.step('采样点时间，期望值：值不为空，实际值：{0}'.format(point_time)):
        assert point_time

    msg_code_direction = get_msg_code_direction(point_index)
    with allure.step('采样点信令方向，期望值：0或1或2，实际值：{0}'.format(msg_code_direction)):
        # print('msg_code_direction: ', msg_code_direction)
        assert msg_code_direction in [0, 1, 2]

    msg_code_info = get_msg_code_info(point_index)
    with allure.step('采样点信令信息，期望值：值不为空，实际值：{0}'.format(msg_code_info)):
        # print('msg_code_info: ', msg_code_info)
        assert msg_code_info

    param_double_value = get_param_double_value(point_index)
    with allure.step('采样点，RSRP的double类型值，期望值：True，实际值：{0}'.format(isinstance(param_double_value, float))):
        # print('param_double_value: ', type(param_double_value))
        assert isinstance(param_double_value, float)

    param_int64_value = get_param_int64_value(point_index)
    with allure.step('采样点，RSRP的int64类型值，期望值：True,实际值：{0}'.format(isinstance(param_int64_value, int))):
        # print('param_int64_value: ', type(param_int64_value))
        assert isinstance(param_int64_value, int)

    real_value_total_count = get_param_real_value_total_count()
    with allure.step('RSRP的真实值总量，期望值：1020，实际值：{0}'.format(real_value_total_count)):
        # print('real_value_total_count: ', real_value_total_count)
        assert 1020 == real_value_total_count

    real_real_value_point_index = get_point_index_by_param_real_value_index()
    with allure.step('RSRP第一个真实值的采样点，期望值：27，实际值：{0}'.format(real_real_value_point_index)):
        # print('real_real_value_point_index: ', real_real_value_point_index)
        assert 27 == real_real_value_point_index

    param_real_value_index = get_param_real_value_index_by_point_index(point_index)
    with allure.step('当前采样点，是RSRP的第几个真实值，期望值：True，实际值：{0}'.format(isinstance(param_real_value_index, int))):
        # print('param_real_value_index: ', param_real_value_index)
        assert isinstance(param_real_value_index, int)

    struct_item_count = get_struct_item_count(point_index)
    with allure.step('结构体小区个数，期望值：大于零，实际值：{0}'.format(struct_item_count)):
        # print('struct_item_count: ', struct_item_count)
        assert 0 <= struct_item_count

    struct_raw_data = get_struct_item(point_index)
    # print('struct_raw_data: ', struct_raw_data)
    num_elements = len(struct_raw_data) // 4
    unpack_struct_data = struct.unpack('<' + 'I' * num_elements, struct_raw_data)
    with allure.step('当前采样点，serviceid为0xE002的结构体小区信息，期望值：值不为空，实际值：{0}'.format(unpack_struct_data)):
        # print('unpack_struct_data: ', unpack_struct_data)
        assert unpack_struct_data

    sub_item_count = get_struct_sub_item_count(point_index)
    with allure.step('当前采样点 ，serviceid为0xE002的结构体子小区数量，期望值：大于零，实际值：{0}'.format(sub_item_count)):
        # print('sub_item_count: ', sub_item_count)
        assert 0 <= sub_item_count

    sub_item_raw_data = get_struct_sub_item(point_index)
    # print('sub_item_raw_data: ', sub_item_raw_data)
    if sub_item_raw_data:
        sub_item_data = struct.unpack('<i?iifff', sub_item_raw_data)
        with allure.step('当前采样点，serviceid为0xE002的结构体子小区信息，期望值：值不为空，实际值：{0}'.format(sub_item_data)):
            # print('sub_item_data: ', sub_item_data)
            assert sub_item_data

    multi_msg_code_info = get_multi_msg_code_info()
    msg_code_standard_info = [{'direction': 2, 'handset_time': 317794071666000, 'msg_code': 4294042133,
                               'pc_time': 317794071666000, 'point_index': 13},
                              {'direction': 2, 'handset_time': 317794071689000, 'msg_code': 4294042121,
                               'pc_time': 317794071689000, 'point_index': 14}]
    with allure.step('采样点 13~15 的msg_code信息，期望值：{0}，实际值：{1}'.format(msg_code_standard_info, multi_msg_code_info)):
        # print('multi_msg_code_info: ', multi_msg_code_info)
        assert msg_code_standard_info == multi_msg_code_info

    multi_param_info = get_multi_param_info()
    param_standard_info = [{'2131165187': [[13, -7167], [27, -7142]]},
                           {'2131165188': [[13, -1036], [27, -1036]]},
                           {'2131165190': [[13, 33227], [27, 32414]]}]
    with allure.step('采样点 13~28 的RSRP、RSRQ、SINR值，期望值：{0}，实际值：{1}'.format(param_standard_info, multi_param_info)):
        # print('multi_param_info: ', multi_param_info)
        assert param_standard_info == multi_param_info

    point_index_data = get_msg_code_point_index_list(TestDCSPlay.total_point)
    standard_index_data = {'count': 7, 'params': [5027, 6997, 9250, 10537, 13363, 13611, 13775]}
    with allure.step('参数code 0xFFF1E003 的出现次数和对应采样点，期望值：{0}，实际值：{1}'.format(standard_index_data, point_index_data)):
        # print('point_index_data: ', point_index_data)
        assert standard_index_data == point_index_data

    type_list = get_exist_msg_code_type_list()
    with allure.step('存在的所有信令类型，期望值：值不为空，实际值：{0}'.format(type_list)):
        # print('type_list: ', type_list)
        assert type_list

    msg_detail_content = get_msg_detail_content(point_index)
    with allure.step('采样点的信令详情，期望值：True，实际值：{0}'.format(isinstance(msg_detail_content, bytes))):
        # print('msg_detail_content: ', type(msg_detail_content))
        assert isinstance(msg_detail_content, bytes)

    msg_content = get_layer3_original_msg_content()
    print('msg_content: ', msg_content)

    multi_event_info = get_multi_event_info()
    print('multi_event_info: ', multi_event_info)

    event_flag_list = get_exist_event_flag_list()
    print('event_flag_list: ', event_flag_list)

    event_property_list = get_event_property_list()
    print('event_property_list: ', event_property_list)

    # UI那边在暂时还未用到
    # multi_sub_item_count = get_struct_multi_sub_item_count()
    # print('multi_sub_item_count: ', multi_sub_item_count)

    # UI那边在暂时还未用到
    # multi_sub_item = get_struct_multi_sub_item()
    # print('multi_sub_item: ', multi_sub_item)

    # UI那边在暂时还未用到
    # event_detail_msg = get_event_detail_msg()
    # print('event_detail_msg: ', event_detail_msg)

    #  LTE 网络数据使用
    # res_set_cell_count = get_set_cell_count_by_set_type()
    # print('res_set_cell_count: ', res_set_cell_count)

    # set_cell_param_value = get_set_cell_param_value_by_set_type()
    # print('set_cell_param_value: ', set_cell_param_value)


msg_detail_content_standard_info = b'<StructXMLDescribe><NR5G-MAC-UL-PhysicalChannelScheduleReport>' \
                                       b'<StructVersion>0</StructVersion><Version>196623</Version>' \
                                       b'<NumRecords>12</NumRecords><Record-List><Record0><Slot>7</Slot>' \
                                       b'<Numerology>1</Numerology><Frame>616</Frame>' \
                                       b'<NumCarrier>1</NumCarrier><Carrier-List><Carrier0>' \
                                       b'<CarrierID>0</CarrierID><PhyChanBitMask>6</PhyChanBitMask>' \
                                       b'<RNTIType>C_RNTI</RNTIType><RNTIValue>0</RNTIValue>' \
                                       b'<AntennaBitmask>0</AntennaBitmask><LongPucchData>' \
                                       b'<NumPucchData>1</NumPucchData><PucchData-List><PucchData0>' \
                                       b'<IsSecondPhychan>0</IsSecondPhychan>' \
                                       b'<PucchFormat>2: PUCCH_FORMAT_F2</PucchFormat>' \
                                       b'<FreqHoppingFlag>0: HOP_MODE_NEITHER</FreqHoppingFlag>' \
                                       b'<StartingRB>97</StartingRB><SecondHopRB>511</SecondHopRB>' \
                                       b'<NumRB>4</NumRB><StartSymbol>13</StartSymbol>' \
                                       b'<NumSymbols>1</NumSymbols><BetaPUCCH>0</BetaPUCCH>' \
                                       b'<BetaDMRS>0</BetaDMRS><M0>0</M0><TimeOCCIndex>0</TimeOCCIndex>' \
                                       b'<iDMRS>0</iDMRS><DftOccLength>0</DftOccLength>' \
                                       b'<DftOccIndex>0</DftOccIndex><UCIRequestBMask>2</UCIRequestBMask>' \
                                       b'<CsfBMask>0</CsfBMask></PucchData0></PucchData-List>' \
                                       b'</LongPucchData><SRSData><NumSRSData>0</NumSRSData></SRSData>' \
                                       b'</Carrier0></Carrier-List></Record0><Record1><Slot>7</Slot>' \
                                       b'<Numerology>1</Numerology><Frame>617</Frame>' \
                                       b'<NumCarrier>1</NumCarrier><Carrier-List><Carrier0>' \
                                       b'<CarrierID>0</CarrierID><PhyChanBitMask>4</PhyChanBitMask>' \
                                       b'<RNTIType>C_RNTI</RNTIType><RNTIValue>0</RNTIValue>' \
                                       b'<AntennaBitmask>0</AntennaBitmask><SRSData>' \
                                       b'<NumSRSData>0</NumSRSData></SRSData></Carrier0></Carrier-List>' \
                                       b'</Record1><Record2><Slot>7</Slot><Numerology>1</Numerology>' \
                                       b'<Frame>618</Frame><NumCarrier>1</NumCarrier><Carrier-List>' \
                                       b'<Carrier0><CarrierID>0</CarrierID>' \
                                       b'<PhyChanBitMask>6</PhyChanBitMask><RNTIType>C_RNTI</RNTIType>' \
                                       b'<RNTIValue>0</RNTIValue><AntennaBitmask>0</AntennaBitmask>' \
                                       b'<LongPucchData><NumPucchData>1</NumPucchData><PucchData-List>' \
                                       b'<PucchData0><IsSecondPhychan>0</IsSecondPhychan>' \
                                       b'<PucchFormat>2: PUCCH_FORMAT_F2</PucchFormat>' \
                                       b'<FreqHoppingFlag>0: HOP_MODE_NEITHER</FreqHoppingFlag>' \
                                       b'<StartingRB>97</StartingRB><SecondHopRB>511</SecondHopRB>' \
                                       b'<NumRB>4</NumRB><StartSymbol>13</StartSymbol>' \
                                       b'<NumSymbols>1</NumSymbols><BetaPUCCH>0</BetaPUCCH>' \
                                       b'<BetaDMRS>0</BetaDMRS><M0>0</M0><TimeOCCIndex>0</TimeOCCIndex>' \
                                       b'<iDMRS>0</iDMRS><DftOccLength>0</DftOccLength>' \
                                       b'<DftOccIndex>0</DftOccIndex><UCIRequestBMask>2</UCIRequestBMask>' \
                                       b'<CsfBMask>0</CsfBMask></PucchData0></PucchData-List>' \
                                       b'</LongPucchData><SRSData><NumSRSData>0</NumSRSData></SRSData>' \
                                       b'</Carrier0></Carrier-List></Record2><Record3><Slot>7</Slot>' \
                                       b'<Numerology>1</Numerology><Frame>619</Frame>' \
                                       b'<NumCarrier>1</NumCarrier><Carrier-List><Carrier0>' \
                                       b'<CarrierID>0</CarrierID><PhyChanBitMask>4</PhyChanBitMask>' \
                                       b'<RNTIType>C_RNTI</RNTIType><RNTIValue>0</RNTIValue>' \
                                       b'<AntennaBitmask>0</AntennaBitmask><SRSData>' \
                                       b'<NumSRSData>0</NumSRSData></SRSData></Carrier0></Carrier-List>' \
                                       b'</Record3><Record4><Slot>7</Slot><Numerology>1</Numerology>' \
                                       b'<Frame>620</Frame><NumCarrier>1</NumCarrier><Carrier-List>' \
                                       b'<Carrier0><CarrierID>0</CarrierID>' \
                                       b'<PhyChanBitMask>6</PhyChanBitMask><RNTIType>C_RNTI</RNTIType>' \
                                       b'<RNTIValue>0</RNTIValue><AntennaBitmask>0</AntennaBitmask>' \
                                       b'<LongPucchData><NumPucchData>1</NumPucchData><PucchData-List>' \
                                       b'<PucchData0><IsSecondPhychan>0</IsSecondPhychan>' \
                                       b'<PucchFormat>2: PUCCH_FORMAT_F2</PucchFormat>' \
                                       b'<FreqHoppingFlag>0: HOP_MODE_NEITHER</FreqHoppingFlag>' \
                                       b'<StartingRB>97</StartingRB><SecondHopRB>511</SecondHopRB>' \
                                       b'<NumRB>4</NumRB><StartSymbol>13</StartSymbol>' \
                                       b'<NumSymbols>1</NumSymbols><BetaPUCCH>0</BetaPUCCH>' \
                                       b'<BetaDMRS>0</BetaDMRS><M0>0</M0><TimeOCCIndex>0</TimeOCCIndex>' \
                                       b'<iDMRS>0</iDMRS><DftOccLength>0</DftOccLength>' \
                                       b'<DftOccIndex>0</DftOccIndex><UCIRequestBMask>2</UCIRequestBMask>' \
                                       b'<CsfBMask>0</CsfBMask></PucchData0></PucchData-List>' \
                                       b'</LongPucchData><SRSData><NumSRSData>0</NumSRSData></SRSData>' \
                                       b'</Carrier0></Carrier-List></Record4><Record5><Slot>7</Slot>' \
                                       b'<Numerology>1</Numerology><Frame>621</Frame>' \
                                       b'<NumCarrier>1</NumCarrier><Carrier-List><Carrier0>' \
                                       b'<CarrierID>0</CarrierID><PhyChanBitMask>4</PhyChanBitMask>' \
                                       b'<RNTIType>C_RNTI</RNTIType><RNTIValue>0</RNTIValue>' \
                                       b'<AntennaBitmask>0</AntennaBitmask><SRSData>' \
                                       b'<NumSRSData>0</NumSRSData></SRSData></Carrier0></Carrier-List>' \
                                       b'</Record5><Record6><Slot>7</Slot><Numerology>1</Numerology>' \
                                       b'<Frame>622</Frame><NumCarrier>1</NumCarrier><Carrier-List>' \
                                       b'<Carrier0><CarrierID>0</CarrierID>' \
                                       b'<PhyChanBitMask>6</PhyChanBitMask><RNTIType>C_RNTI</RNTIType>' \
                                       b'<RNTIValue>0</RNTIValue><AntennaBitmask>0</AntennaBitmask>' \
                                       b'<LongPucchData><NumPucchData>1</NumPucchData><PucchData-List>' \
                                       b'<PucchData0><IsSecondPhychan>0</IsSecondPhychan>' \
                                       b'<PucchFormat>2: PUCCH_FORMAT_F2</PucchFormat>' \
                                       b'<FreqHoppingFlag>0: HOP_MODE_NEITHER</FreqHoppingFlag>' \
                                       b'<StartingRB>97</StartingRB><SecondHopRB>511</SecondHopRB>' \
                                       b'<NumRB>4</NumRB><StartSymbol>13</StartSymbol>' \
                                       b'<NumSymbols>1</NumSymbols><BetaPUCCH>0</BetaPUCCH>' \
                                       b'<BetaDMRS>0</BetaDMRS><M0>0</M0><TimeOCCIndex>0</TimeOCCIndex>' \
                                       b'<iDMRS>0</iDMRS><DftOccLength>0</DftOccLength>' \
                                       b'<DftOccIndex>0</DftOccIndex><UCIRequestBMask>2</UCIRequestBMask>' \
                                       b'<CsfBMask>0</CsfBMask></PucchData0></PucchData-List>' \
                                       b'</LongPucchData><SRSData><NumSRSData>0</NumSRSData></SRSData>' \
                                       b'</Carrier0></Carrier-List></Record6><Record7><Slot>7</Slot>' \
                                       b'<Numerology>1</Numerology><Frame>623</Frame>' \
                                       b'<NumCarrier>1</NumCarrier><Carrier-List><Carrier0>' \
                                       b'<CarrierID>0</CarrierID><PhyChanBitMask>4</PhyChanBitMask>' \
                                       b'<RNTIType>C_RNTI</RNTIType><RNTIValue>0</RNTIValue>' \
                                       b'<AntennaBitmask>0</AntennaBitmask><SRSData>' \
                                       b'<NumSRSData>0</NumSRSData></SRSData></Carrier0></Carrier-List>' \
                                       b'</Record7><Record8><Slot>7</Slot><Numerology>1</Numerology>' \
                                       b'<Frame>624</Frame><NumCarrier>1</NumCarrier><Carrier-List>' \
                                       b'<Carrier0><CarrierID>0</CarrierID>' \
                                       b'<PhyChanBitMask>6</PhyChanBitMask><RNTIType>C_RNTI</RNTIType>' \
                                       b'<RNTIValue>0</RNTIValue><AntennaBitmask>0</AntennaBitmask>' \
                                       b'<LongPucchData><NumPucchData>1</NumPucchData><PucchData-List>' \
                                       b'<PucchData0><IsSecondPhychan>0</IsSecondPhychan>' \
                                       b'<PucchFormat>2: PUCCH_FORMAT_F2</PucchFormat>' \
                                       b'<FreqHoppingFlag>0: HOP_MODE_NEITHER</FreqHoppingFlag>' \
                                       b'<StartingRB>97</StartingRB><SecondHopRB>511</SecondHopRB>' \
                                       b'<NumRB>4</NumRB><StartSymbol>13</StartSymbol>' \
                                       b'<NumSymbols>1</NumSymbols><BetaPUCCH>0</BetaPUCCH>' \
                                       b'<BetaDMRS>0</BetaDMRS><M0>0</M0><TimeOCCIndex>0</TimeOCCIndex>' \
                                       b'<iDMRS>0</iDMRS><DftOccLength>0</DftOccLength>' \
                                       b'<DftOccIndex>0</DftOccIndex><UCIRequestBMask>2</UCIRequestBMask>' \
                                       b'<CsfBMask>0</CsfBMask></PucchData0></PucchData-List>' \
                                       b'</LongPucchData><SRSData><NumSRSData>0</NumSRSData></SRSData>' \
                                       b'</Carrier0></Carrier-List></Record8><Record9><Slot>7</Slot>' \
                                       b'<Numerology>1</Numerology><Frame>625</Frame>' \
                                       b'<NumCarrier>1</NumCarrier><Carrier-List><Carrier0>' \
                                       b'<CarrierID>0</CarrierID><PhyChanBitMask>4</PhyChanBitMask>' \
                                       b'<RNTIType>C_RNTI</RNTIType><RNTIValue>0</RNTIValue>' \
                                       b'<AntennaBitmask>0</AntennaBitmask><SRSData><NumSRSData>0' \
                                       b'</NumSRSData></SRSData></Carrier0></Carrier-List></Record9' \
                                       b'><Record10><Slot>7</Slot><Numerology>1</Numerology><Frame>626' \
                                       b'</Frame><NumCarrier>1</NumCarrier><Carrier-List><Carrier0' \
                                       b'><CarrierID>0</CarrierID><PhyChanBitMask>6</PhyChanBitMask' \
                                       b'><RNTIType>C_RNTI</RNTIType><RNTIValue>0</RNTIValue' \
                                       b'><AntennaBitmask>0</AntennaBitmask><LongPucchData><NumPucchData' \
                                       b'>1</NumPucchData><PucchData-List><PucchData0><IsSecondPhychan>0' \
                                       b'</IsSecondPhychan><PucchFormat>2: ' \
                                       b'PUCCH_FORMAT_F2</PucchFormat><FreqHoppingFlag>0: ' \
                                       b'HOP_MODE_NEITHER</FreqHoppingFlag><StartingRB>97</StartingRB' \
                                       b'><SecondHopRB>511</SecondHopRB><NumRB>4</NumRB><StartSymbol>13' \
                                       b'</StartSymbol><NumSymbols>1</NumSymbols><BetaPUCCH>0</BetaPUCCH' \
                                       b'><BetaDMRS>0</BetaDMRS><M0>0</M0><TimeOCCIndex>0</TimeOCCIndex' \
                                       b'><iDMRS>0</iDMRS><DftOccLength>0</DftOccLength><DftOccIndex>0' \
                                       b'</DftOccIndex><UCIRequestBMask>2</UCIRequestBMask><CsfBMask>0' \
                                       b'</CsfBMask></PucchData0></PucchData-List></LongPucchData' \
                                       b'><SRSData><NumSRSData>0</NumSRSData></SRSData></Carrier0' \
                                       b'></Carrier-List></Record10><Record11><Slot>7</Slot><Numerology>1' \
                                       b'</Numerology><Frame>627</Frame><NumCarrier>1</NumCarrier' \
                                       b'><Carrier-List><Carrier0><CarrierID>0</CarrierID><PhyChanBitMask' \
                                       b'>4</PhyChanBitMask><RNTIType>C_RNTI</RNTIType><RNTIValue>0' \
                                       b'</RNTIValue><AntennaBitmask>0</AntennaBitmask><SRSData' \
                                       b'><NumSRSData>0</NumSRSData></SRSData></Carrier0></Carrier-List' \
                                       b'></Record11></Record-List></NR5G-MAC-UL' \
                                       b'-PhysicalChannelScheduleReport></StructXMLDescribe>'


def check_msg_detail_content():
    msg_detail_content = get_msg_detail_content(1)
    with allure.step('检查采样点 1 的的信令详情'):
        with allure.step(
                '断言信令详情，期望值：{0}实际值：{1}'.format(msg_detail_content_standard_info, msg_detail_content)):
            assert msg_detail_content_standard_info == msg_detail_content


@allure.feature('DCSPlay业务测试')
class TestDCSPlay:
    def setup_class(self):
        TestDCSPlay.package_project = PackageUnpack(dll_path)
        pubsub.subscribe('PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest-cmdrequest')

        device_id = get_device_id_from_redis()
        TestDCSPlay.dcs_daemon_chanel = device_id + '-DCSDaemon-cmdrequest'
        print('dcs_daemon_chanel: ', TestDCSPlay.dcs_daemon_chanel)

        TestDCSPlay.dcs_play_file = os.path.join(test_data_path, 'DCSPlay_demo.ddib')

        with allure.step('启动回放服务'):
            print('发送命令给精灵服务，启动回放服务')
            TestDCSPlay.dcs_play_test_port = start_dcs_play_get_test_port()
            print('dcs_play_test_port: ', TestDCSPlay.dcs_play_test_port)

        TestDCSPlay.dcs_play_chanel = device_id + '-DCSPlay-{0}-cmdrequest'.format(TestDCSPlay.dcs_play_test_port)
        print('dcs_play_chanel: ', TestDCSPlay.dcs_play_chanel)

        with allure.step('开始回放 {0} 文件'.format(TestDCSPlay.dcs_play_file)):
            print('开始回放文件：', TestDCSPlay.dcs_play_file)
            send_file_play_cmd()

        # 数据生成
        # with allure.step('回放服务，生成 check 标准数据'):
        #     check_point_list = [0, 13, 14, 27, 18616]
        #     generate_std_info(sorted(check_point_list))
        #     out_std_info()

        with allure.step('获取总采样点'):
            TestDCSPlay.total_point = get_total_point_count()
            print('total_point: ', TestDCSPlay.total_point)
            with allure.step('期望值：18617，实际值：{0}'.format(TestDCSPlay.total_point)):
                assert 18617 == TestDCSPlay.total_point

    def teardown_class(self):
        pubsub.unsubscribe('PFS-EEFB41C0342CB49570EEB4DED2CBC588-CN.GuangZhou.Zhuhai-AutoTest-cmdrequest')

    @allure.step('ddib数据正向回放数据检查')
    def test_datasets_replay_data_check(self):
        check_msg_detail_content()
        check_list.append(TestDCSPlay.total_point - 1)
        for point in check_list:
            with allure.step('检查采样点：{0}的信息'.format(point)):
                datasets_interface_call_data_check(point)

    @allure.step('ddib数据多采样点数据正向回放')
    def test_datasets_forward_replay(self):
        # 数据回放
        with allure.step('数据正向回放'):
            for point in range(15000, 15010):
                with allure.step('回放采样点：{0}的信息'.format(point)):
                    datasets_interface_call_forward_replay(point)


if __name__ == "__main__":
    new_test = TestDCSPlay()
    new_test.setup_class()
    new_test.test_data_replay()

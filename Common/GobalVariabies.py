# -*- coding:utf-8 -*-
import inspect
import os

from Common.Operation import *

PROJECT_BASE = os.path.abspath(os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), ".."))

# 配置文件xml路径
xml_path = os.path.join(PROJECT_BASE, r'TestData\DCSServerMgrcfg')
config_xml_path = os.path.join(xml_path, 'DCSServerMgrcfg.xml')

test_data_path = os.path.dirname(xml_path)

# redis 对象
# f_redis = RedisOperations(host='172.16.23.148')
f_redis = RedisOperations(host='127.0.0.1')
f_redis.connect()

# redis对象
redis_conn = redis.Redis(host='127.0.0.1', port=6379)
pubsub = redis_conn.pubsub()

# pg 对象
# pg_project = PostgresOperations(host='172.16.23.148')
pg_project = PostgresOperations(host='172.16.21.65')
pg_project.pg_connect()

# ui_service 对象
ui_service_project = WebSocket('ws://127.0.0.1:2022/')

# 当前所在驱动器
cur_drive = get_current_drive()

# 本地目的目录
dcs_path = os.path.join(cur_drive, r'\Auto_Test_DCS')
if not os.path.exists(dcs_path):
    os.makedirs(dcs_path)

# 本地临时目录
local_tmp_path = os.path.join(cur_drive, r'\auto_test_tmp_path')
if not os.path.exists(local_tmp_path):
    os.makedirs(local_tmp_path)

dll_path = os.path.join(os.path.join(dcs_path, r'dcs_build\bin\MakeAndUnPackage.dll'))
# package_project = PackageUnpack(dll_path)

# 获取dcs服务相关信息
exe_path, test_port_list, process_name_list = parse_xml_get_test_port_list(config_xml_path)

# UI_service 命令
ui_start_work_cmd = {"API": "StartWork", "Params": {'TestPort': 0, 'RequestId': ''}}
ui_update_test_plan_cmd = {"API": "UpdateTestplan", "Params": {"Name": "", "TimeZone": "", "TestPlanXml": "", "Origin": 0,
                                         "TestPort": int(0), "RequestId": "", "IsTest": True}}
ui_start_test_cmd = {"API": "StartTestPlan", "Params": {"FileName": "", "IsFileCut": 0, "TestPort": 0, "RequestId": ""}}


def ui_send(send_cmd, send_port=None):
    if send_port:
        send_cmd['Params']['TestPort'] = int(send_port)
    ui_service_project.send(json.dumps(send_cmd))


def ui_send_get_res(send_cmd, send_port=None):
    if send_port:
        send_cmd['Params']['TestPort'] = int(send_port)
    ui_service_project.send_get_res(json.dumps(send_cmd))


def get_test_port_list_from_xml(get_path=config_xml_path):
    return parse_xml_get_test_port_list_by_server_name(get_path)


def get_device_id_from_redis():
    return f_redis.hkeys('device_list')[0]


def get_all_run_process(device_id):
    process_list_hash_name = device_id + '-DCSDaemon-process_list'
    process_data = f_redis.hgetall(process_list_hash_name)
    tmp_list = []

    for process_name in process_data:
        if 'Running' == process_data[process_name] and 'DCSDeviceServer' in process_name:
            tmp_list.append(process_name)

    return tmp_list


def check_ip(_ip, des_ip):
    dos_cmd = 'ping {0} -S {1}'.format(des_ip, _ip)
    result = subprocess.run(dos_cmd, capture_output=True, text=True)

    if result.returncode == 0:
        return True
    return False


def check_module(hash_list, ping_des_ip='10.20.6.200'):
    tmp_list = []
    for hash_name in hash_list:
        out_data_flag = int(f_redis.hget(hash_name, 'module_diag_have_out_data'))
        print('out_data_flag: ', out_data_flag)
        print('type: ', type(out_data_flag))
        if out_data_flag:
            module_ip = f_redis.hget(hash_name, 'module_netadopt_ipv4')
            print('module_ip: ', module_ip)
            if check_ip(module_ip, ping_des_ip):
                port = int(hash_name[hash_name.rfind('-') + 1:])
                tmp_list.append(port)
                # print('hash_name: ', hash_name)
                # print('port: ', port)

    return tmp_list


def get_can_use_module_port(device_id):
    process_list_hash_name = device_id + '-DCSDaemon-process_list'
    process_data = f_redis.hgetall(process_list_hash_name)
    service_status_list = []
    ip_status_list = []

    for service_name in process_data:
        if 'DCSDataSets' in service_name:
            server_status = f_redis.hget(service_name, 'server_status')
            if 'Servering' == server_status:
                port = int(service_name[service_name.rfind('_'):])
                service_status_list.append(port)

        # if 'DCSDeviceServer' in service_name:
        #     get_ip = f_redis.hget(service_name, 'module_netadopt_ipv4')
        #     if get_ip:
        #         port = int(service_name[service_name.rfind('_'):])
        #         ip_status_list.append(port)

    return service_status_list

    # return sorted(list(set(service_status_list) & set(ip_status_list)))


def generate_start_service_xml(xml_file_name, port_list):
    config_xml = os.path.join(local_tmp_path, xml_file_name)
    if os.path.exists(config_xml):
        os.remove(config_xml)

    copy_file(os.path.join(xml_path, 'DCSServerMgrcfg_template.xml'), config_xml)
    print('exe_path: ', exe_path)
    for port in port_list:
        ParseXml.add_node(config_xml, 'server', exe_path, port)

    return config_xml


def pub_json_cmd_to_redis_chanel(package_project, cmd_json, pub_sub, pub_chanel):
    packed_json = package_project.package_json(json.dumps(cmd_json), b'')
    f_redis.pub(pub_chanel, packed_json)
    for message in pub_sub.listen():
        print('message: ', message)
        if 'message' == message['type']:
            print('接收到的数据为：', message['data'])
            return json.loads(package_project.unpack_json(message['data']))


def pub_json_cmd_to_redis_chanel_get_raw(package_project, cmd_json, pub_sub, pub_chanel):
    packed_json = package_project.package_json(json.dumps(cmd_json), b'')
    f_redis.pub(pub_chanel, packed_json)
    for message in pub_sub.listen():
        print('message: ', message)
        if 'message' == message['type']:
            print('接收到的数据为：', message['data'])
            return package_project.unpack_json_and_raw(message['data'])


def update_test_plan(test_plan_id, device_id):
    get_test_plan_cmd = 'select "test_plan_data"."test_plan_xml" from ' \
                        '"public"."test_plan_data" WHERE ' \
                        '"test_plan_data"."id" = {0}'.format(test_plan_id)
    print('get_test_plan_cmd: ', get_test_plan_cmd)
    serial_test_plan_data = pg_project.pg_run_sql_fetchall(get_test_plan_cmd)

    pg_insert_cmd = 'INSERT INTO "public"."testplan_history" (unified_xml, dev_id) VALUES (\'{0}\', \'{1}\')'.format(
        serial_test_plan_data[0][0], device_id)
    pg_project.pg_insert_data(pg_insert_cmd)

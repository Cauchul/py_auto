import shutil
import socket
import subprocess
import allure
import psutil
import time
import json
import urllib.parse

import py7zr
import redis
import sqlalchemy
import psycopg2
import os
import pandas as pd
import xml.etree.ElementTree as et

import websocket
from sqlalchemy import table, text, engine, MetaData
from sqlalchemy.orm import sessionmaker
from multiprocessing import Process
from numpy import *
from pytest_assume.plugin import assume
import ctypes
from ctypes import *
from ftplib import FTP
from datetime import datetime
import binascii


def clean_up_test_case_runtime_env():
    process_name_list = ['DCSDaemonExe.exe', 'logger_server.exe', 'DCSUIService.exe',
                         'DCSTestMgr.exe', 'DCSTests.exe', 'power_server.exe', 'DCSSystemMgr.exe',
                         'DCSSoundMgr.exe', 'DCSMos.exe', 'DCSSoundCard.exe', 'DcsDeviceServerExe.exe',
                         'DCSDataSets.exe', 'DCSTestSchedule.exe', 'PFSClient.exe', 'DCSPlay.exe', 'iperf.exe']
    for process_name in process_name_list:
        for proc in psutil.process_iter():
            if proc.name() == process_name:
                proc.kill()


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    _ip = s.getsockname()[0]
    s.close()
    return _ip


def start_service(exe_file_path, daemon_xml_path):
    cmd = r'{0}\DCSDaemonExe.exe -xmlConfigPath:{1} '.format(exe_file_path, daemon_xml_path)
    with allure.step('启动 DCS 服务，命令为: {0}'.format(cmd)):
        subprocess.Popen(cmd)


def parse_xml_get_common(config_xml, node_name='redis'):
    tree_root_config_xml = ParseXml.get_root_by_xml_name(config_xml)
    servers_node = tree_root_config_xml.find('common')
    redis_node = servers_node.find(node_name)
    print('{0} host: {1}'.format(node_name, redis_node.attrib['host']))
    return redis_node.attrib['host']


def parse_xml_get_test_port_list_by_server_name(config_xml, server_name='DCSDataSets'):
    port_list = []
    tree_root_config_xml = ParseXml.get_root_by_xml_name(config_xml)
    servers_node = tree_root_config_xml.find('servers')
    for neighbor in servers_node:
        if server_name == neighbor.attrib['name']:
            port_list.append(neighbor.attrib['testPort'])
    print('port_list', port_list)
    return port_list


def parse_xml_get_test_port_list(config_xml):
    parse_process_list = ['DCSDaemonExe.exe', 'logger_server.exe']
    port_list = []
    exe_file_path = ''
    tree_root_config_xml = ParseXml.get_root_by_xml_name(config_xml)
    servers_node = tree_root_config_xml.find('servers')
    for neighbor in servers_node:
        if 'DCSDeviceServer' == neighbor.attrib['name']:
            port_list.append(neighbor.attrib['testPort'])
    if parse_process_list is not None:
        run_flag = True
        for neighbor in tree_root_config_xml[1]:
            if 'DCSDataSets.exe' not in os.path.basename(neighbor.attrib['path']) and run_flag:
                run_flag = False
                exe_file_path = os.path.dirname(neighbor.attrib['path'])
            # print('neighbor', neighbor.attrib['path'].split('\\')[-1])
            # parse_process_list.append(neighbor.attrib['path'].split('\\')[-1])
            parse_process_list.append(os.path.basename(neighbor.attrib['path']))
    return exe_file_path, port_list, parse_process_list


def get_cpu_and_memory_usage(process_name):
    time_int = int(round(time.time() * 1000))
    _time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time_int / 1000))
    system_per_cpu_percentage = psutil.cpu_percent(interval=1, percpu=True)
    available_memory = str((psutil.virtual_memory().available / 1048576).__round__(2))
    for proc in psutil.process_iter(['name', 'cpu_percent', 'pid']):
        with proc.oneshot():
            if psutil.pid_exists(proc.pid):
                if proc.name() == process_name:
                    process_cpu_usage = proc.cpu_percent(interval=1) / psutil.cpu_count().__round__(2)
                    process_used_memory = str((proc.memory_full_info().uss / 1048576).__round__(2))
                    break
    data = [_time, system_per_cpu_percentage, process_cpu_usage, available_memory, process_used_memory]
    return data


def run_bat_cmd(run_cmd):
    os.system(run_cmd)


def clear_dcs_service():
    """
    清理 UIService，logger_service 以外的 DCS 所有服务
    :return:
    """
    clean_process_name_list = ['DCSDaemonExe.exe', 'DCSTestMgr.exe', 'DCSTests.exe', 'power_server.exe',
                         'DCSSystemMgr.exe', 'DCSSoundMgr.exe', 'DCSMos.exe', 'DCSSoundCard.exe',
                         'DcsDeviceServerExe.exe', 'DCSDataSets.exe', 'DCSTestSchedule.exe']

    for process_name in clean_process_name_list:
        for proc in psutil.process_iter():
            if proc.name() == process_name:
                proc.kill()
        # clear_cmd = 'taskkill /F /im {0}'.format(process_name)
        # print('clear_cmd: ', clear_cmd)
        # os.system(clear_cmd)


def run_bat_cmd_start_thread(run_cmd):
    os.popen(run_cmd)
    # subprocess.Popen(run_cmd)


def get_pid(name):
    pids = psutil.process_iter()
    for pid in pids:
        if pid.name() == name:
            print(pid.pid)
            return pid.pid


def check_process_is_exist(process_name):
    check_process_bat_cmd = 'tasklist|find /i \"{0}\"'.format(process_name)
    if 0 == os.system(check_process_bat_cmd):
        return True
    return False

# def check_process_is_exist(name):
#     pl = psutil.pids()
#     for pid in pl:
#         try:
#             if psutil.Process(pid).name() == name:
#                 print(pid)
#                 return True
#         except:
#             return False
#     else:
#         return False


def get_path_by_process_name(name):
    p = psutil.Process(get_pid(name))
    print(os.path.dirname(p.exe()))
    return os.path.dirname(p.exe())


process_list = []
cpu_percent_usage_list = []


def dead_loop():
    while True:
        pass


def start_dead_loop():
    print('---start_dead_loop---')
    for n in range(5):
        p = Process(target=dead_loop)
        p.daemon = True
        p.start()
        process_list.append(p)


def start_cpu_full_load():
    while psutil.cpu_percent(interval=0.1) < 99.5:
        start_dead_loop()
        with allure.step('启动负载进程，当前cpu占用率为：{0}，'.format(psutil.cpu_percent(interval=0.1))):
            print('---start_cpu_full_load---')


def stop_cpu_full_load():
    for p in process_list:
        p.kill()
        if p.is_alive():
            p.terminate()
        with allure.step('释放负载进程，当前cpu占用率为：{0}'.format(psutil.cpu_percent(interval=0.1))):
            print('---stop_cpu_full_load---')
    with allure.step('负载进程释放结束，cpu占用率为：{0}'.format(psutil.cpu_percent(interval=0.1))):
        pass


count = 0


def run_cpu_full_load_main(limit_num=2):
    if limit_num < 0:
        return
    global count
    print('---run_cpu_full_load_main---')
    start = time.time()
    start_cpu_full_load()
    while True:
        if count > 1:
            if 2 == limit_num:
                with assume:
                    with allure.step('cpu未满载，超时退出'):
                        print('cpu未满载，超时退出')
                        assert 1 == 0
            return
        print('cur_cpu_usage: ', psutil.cpu_percent(interval=0.1))
        cpu_percent_usage_list.append(psutil.cpu_percent(interval=0.1))
        if time.time() - start > 300 and 95 < mean(cpu_percent_usage_list):
            with allure.step('持续检测300s，cpu占用率采样点中位数超过95，满载成功'):
                print('cpu满载成功. 持续检测时间: ', (time.time() - start).__round__(0))
            return
        elif time.time() - start > 300 and 95 > mean(cpu_percent_usage_list):
            count = count + 1
            if count < 2:
                with allure.step('cpu使用率小于%95，重新启动满载'):
                    print('cpu使用率小于95,重新启动满载')
                run_cpu_full_load_main(limit_num - 1)
        time.sleep(2)


def unzip_7z_file(zip_path, dst_path):
    if not os.path.exists(dst_path):
        os.mkdir(dst_path)
    with py7zr.SevenZipFile(zip_path, 'r') as archive:
        archive.extractall(dst_path)


def get_today_time():
    return datetime.now().date().strftime('%Y%m%d')


def get_current_drive():
    """
    :return: 当前驱动器
    """
    return os.path.splitdrive(os.getcwd())[0]


def delete_directory(dir_path):
    shutil.rmtree(dir_path, ignore_errors=True)


def copy_file(src_file_or_path, dst_path):
    if os.path.isfile(src_file_or_path):
        shutil.copy2(src_file_or_path, dst_path)
    elif os.path.isdir(src_file_or_path):
        shutil.copytree(src_file_or_path, dst_path, copy_function=shutil.copy2)


class RedisOperations:

    def __init__(self, host='127.0.0.1', port=6379, db=0, pwd=''):
        self._host = host
        self._port = port
        self._db = db
        self._password = pwd
        self._redis_conn = None
        self._redis_blocking_conn = None
        self._connect_type = None
        self._keys = None

    def connect(self):
        try:
            self._redis_conn = redis.Redis(host=self._host, port=self._port, db=self._db, password=self._password,
                                           decode_responses=True)
            self._keys = self._redis_conn.keys()
            self._connect_type = 'Single'
        except redis.RedisError as error:
            raise error

    def blocking_connect(self):
        try:
            pool = redis.BlockingConnectionPool(host=self._host, port=self._port, db=self._db, password=self._password,
                                                max_connections=5, socket_connect_timeout=10, decode_responses=True)
            self._redis_blocking_conn = redis.Redis(connection_pool=pool)
            self._keys = self._redis_blocking_conn.keys()
            self._connect_type = 'Blocking'
        except redis.RedisError as error:
            raise error

    def url_connect(self):
        try:
            _url = r"redis://default:" + self._password + "@" + self._host + ":" + str(self._port) + "/" + str(self._db)
            print(_url)
            self._redis_conn = redis.from_url(_url, decode_responses=True)
            self._keys = self._redis_conn.keys()
            self._connect_type = 'url'
        except redis.RedisError as error:
            raise error

    def get(self, key=""):
        if key == "":
            return False
        else:
            if self._connect_type == 'Single' or self._connect_type == 'url':
                return self._redis_conn.get(key)
            elif self._connect_type == 'Blocking':
                return self._redis_blocking_conn.get(key)
            else:
                return False

    def set(self, set_key="", value=""):
        try:
            if key != "":
                if self._connect_type == 'Single' or self._connect_type == 'url':
                    return redis.client.bool_ok(self._redis_conn.set(set_key, value))
                elif self._connect_type == 'Blocking':
                    return self._redis_blocking_conn.set(set_key, value)
                else:
                    return False
            else:
                return False
        except redis.RedisError as error:
            raise error

    def hset(self, hash_name='', hash_key='', value=''):
        try:
            if hash_key != "":
                if self._connect_type == 'Single' or self._connect_type == 'url':
                    return self._redis_conn.hset(hash_name, hash_key, value)
                elif self._connect_type == 'Blocking':
                    return self._redis_blocking_conn.hset(hash_name, hash_key, value)
                else:
                    return False
            else:
                return False
        except redis.RedisError as error:
            raise error

    def hget(self, hash_name='', hash_key=''):
        try:
            if hash_key != "":
                if self._connect_type == 'Single' or self._connect_type == 'url':
                    return self._redis_conn.hget(hash_name, hash_key)
                elif self._connect_type == 'Blocking':
                    return self._redis_blocking_conn.hget(hash_name, hash_key)
                else:
                    return False
            else:
                return False
        except redis.RedisError as error:
            raise error

    def hkeys(self, hash_name=''):
        try:
            if self._connect_type == 'Single' or self._connect_type == 'url':
                return self._redis_conn.hkeys(hash_name)
            elif self._connect_type == 'Blocking':
                return self._redis_blocking_conn.hkeys(hash_name)
            else:
                return False
        except redis.RedisError as error:
            raise error

    def hgetall(self, hash_name=''):
        try:
            if self._connect_type == 'Single' or self._connect_type == 'url':
                return self._redis_conn.hgetall(hash_name)
            elif self._connect_type == 'Blocking':
                return self._redis_blocking_conn.hgetall(hash_name)
            else:
                return False
        except redis.RedisError as error:
            raise error

    def pub(self, chanel="", value=""):
        if self._connect_type == 'Single' or self._connect_type == 'url':
            self._redis_conn.publish(chanel, value)
        elif self._connect_type == 'Blocking':
            self._redis_blocking_conn.publish(chanel, value)

    def sub(self, chanel=""):
        sub_h = None
        if self._connect_type == 'Single' or self._connect_type == 'url':
            sub_h = self._redis_conn.pubsub()
        elif self._connect_type == 'Blocking':
            sub_h = self._redis_blocking_conn.pubsub()
        sub_h.subscribe(chanel)
        return sub_h.listen()

    def pubsub(self):
        if self._connect_type == 'Single' or self._connect_type == 'url':
            return self._redis_conn.pubsub()
        elif self._connect_type == 'Blocking':
            return self._redis_blocking_conn.pubsub()

    def delete(self, hash_name=''):
        if self._connect_type == 'Single' or self._connect_type == 'url':
            self._redis_conn.delete(hash_name)
        elif self._connect_type == 'Blocking':
            self._redis_blocking_conn.delete(hash_name)

    def get_redis_keys(self):
        # return self._keys
        if self._connect_type == 'Single' or self._connect_type == 'url':
            return self._redis_conn.keys()
        elif self._connect_type == 'Blocking':
            return self._redis_blocking_conn.keys()


class PostgresOperations:
    def __init__(self, host='127.0.0.1', port='5432', user='postgres', pwd='123456', db='postgres'):
        self._host = host
        self._port = port
        self._db = db
        self._user = user
        self._pwd = pwd
        self._conn = None
        self._db_session = None
        self._connection_str = "postgresql+psycopg2://" + self._user + ":" + self._pwd + "@" + self._host + ':' + self._port + "/" + self._db
        self.conn_string = "host=" + self._host + " port=" + self._port + " dbname=" + self._db + " user=" + self._user + " password=" + self._pwd
        self._engine = engine.create_engine(self._connection_str)

    def pg_connect(self):
        self._conn = psycopg2.connect(self.conn_string)
        self._db_session = sessionmaker(bind=self._engine)

    def pg_select_data(self, query_sql):
        try:
            if query_sql != '':
                return pd.read_sql_query(query_sql, self._engine)
        except Exception as error:
            raise error

    def pg_run_sql(self, cmd_sql):
        try:
            if cmd_sql != '':
                cursor = self._conn.cursor()
                cursor.execute(cmd_sql)
                self._conn.commit()
        except Exception as error:
            raise error

    def pg_insert_data(self, insert_sql):
        try:
            if insert_sql != '':
                cursor = self._conn.cursor()
                cursor.execute(insert_sql)
                self._conn.commit()
                # get_id_sql_cmd = 'SELECT max("Test"."Id") from "public"."Test";'
                # cursor.execute(get_id_sql_cmd)
                # data_id = cursor.fetchone()
                # self._conn.commit()
                # print('data_id: ', data_id[0])
                # return data_id[0]
        except Exception as error:
            raise error

    def pg_run_sql_fetchone(self, sql_cmd):
        try:
            if sql_cmd != '':
                result_data = self._engine.execute(sql_cmd).fetchone()
                return result_data
        except Exception as error:
            raise error

    def pg_run_sql_fetchall(self, sql_cmd):
        try:
            if sql_cmd != '':
                result_data = self._engine.execute(sql_cmd).fetchall()
                return result_data
        except Exception as error:
            raise error

    def pg_run_sql_generate_xml(self, sql_cmd, xml_name, pg_column_name):
        pg_data = self.pg_select_data(sql_cmd)
        with open(xml_name, 'w') as f_p:
            f_p.write(pg_data[pg_column_name][0])

    def pg_close(self):
        # self._db_session.close()
        self._conn.close()


class StartInfoStruct(Structure):
    _fields_ = [
        ('local_if', c_char),
        ('parent_processid', c_int32),
        ('host_if', c_char),
        ('packet_size', c_int32),
        ('ttl', c_int32),
        ('ping_timeout_ms', c_int32)
    ]


class PackageUnpack:
    def __init__(self, dll_path):
        self.dll_handle = cdll.LoadLibrary(dll_path)

    def package_json(self, json_str, raw_data=b''):
        # data_size = len(raw_data)
        json_str_buf = create_string_buffer(bytes(str(json_str), encoding='utf-8'))
        raw_data_buf = create_string_buffer(bytes(raw_data))
        data_len = c_int32(4096000)
        res_package_data = create_string_buffer(b'', 4096000)
        print('发送的json命令为: ', json_str)
        # print('发送的json长度为： ', len(json_str))
        if self.dll_handle.Init():
            self.dll_handle.MakePackage.restype = c_bool
            returned_package = self.dll_handle.MakePackage(json_str_buf, c_int32(len(json_str)), raw_data_buf,
                                                           c_int32(len(raw_data)), c_bool(True),
                                                           byref(res_package_data), byref(data_len))
            print('封包数据长度: ', data_len.value)
            if returned_package:
                return res_package_data.raw[:data_len.value]
            return None
        else:
            return None

    def unpack_json(self, raw_data):
        json_len = c_int32(4096000)
        raw_len = c_int32(4096000)
        unpack_json_data = create_string_buffer(b'', 4096000)
        make_raw_data_buf = create_string_buffer(raw_data)
        unpack_raw_data = create_string_buffer(b'', 4096000)
        res = self.dll_handle.UnPackage(make_raw_data_buf, c_int32(len(raw_data)), byref(unpack_json_data),
                                        byref(json_len), byref(unpack_raw_data), byref(raw_len))
        print('解出的json命令长度: ', json_len.value)
        # print('解包出来的json命令为： ', unpack_json_data.raw[:json_len.value].decode('utf-8').strip())
        # print('解包raw长度： ', raw_len.value)
        # print('解包出来的raw为： ', unpack_raw_data.raw[:raw_len.value].decode('utf-8'))
        # print('解包出来的raw为： ', unpack_raw_data.raw[:raw_len.value])
        if res:
            return unpack_json_data.raw[:json_len.value].decode('utf-8').strip()

    def unpack_json_and_raw(self, raw_data):
        json_len = c_int32(4096000)
        raw_len = c_int32(4096000)
        unpack_json_data = create_string_buffer(b'', 4096000)
        make_raw_data_buf = create_string_buffer(raw_data)
        unpack_raw_data = create_string_buffer(b'', 4096000)
        res = self.dll_handle.UnPackage(make_raw_data_buf, c_int32(len(raw_data)), byref(unpack_json_data),
                                        byref(json_len), byref(unpack_raw_data), byref(raw_len))
        print('解出的json命令长度: ', json_len.value)
        # print('解包出来的json命令为： ', unpack_json_data.raw[:json_len.value].decode('utf-8').strip())
        # print('解包raw长度： ', raw_len.value)
        # print('解包出来的raw为： ', unpack_raw_data.raw[:raw_len.value].decode('utf-8'))
        print('解包出来的raw为： ', unpack_raw_data.raw[:raw_len.value])
        if res:
            return json.loads(unpack_json_data.raw[:json_len.value].decode('utf-8').strip()), unpack_raw_data.raw[:raw_len.value]

    def release_handle(self):
        # if self.dll_handle is not None:
        if self.dll_handle:
            self.dll_handle.Uninit()


class ParseXml:
    @staticmethod
    def get_root_by_xml_name(xml_name):
        xml_file = open(xml_name)
        parse_tree = et.parse(xml_file)
        return parse_tree.getroot()

    @staticmethod
    def get_root_by_element_name(root_node, el_name):
        for node in root_node.iter():
            if el_name == node.tag:
                return node

    @staticmethod
    def parse_xml_data_to_dict_by_node(root_node):
        res_dict = {}
        for node in root_node:
            res_dict[node.tag] = node.text
        return res_dict

    @staticmethod
    def add_node(config_xml, attr_name, process_path, test_port):
        service_name_list = ['DCSSoundCard.exe', 'DcsDeviceServerExe.exe', r'Datasets\DCSDataSets.exe',
                             'DCSTestSchedule.exe']
        name_swap_dict = {'DCSSoundCard.exe': 'DCSSoundCard', 'DcsDeviceServerExe.exe': 'DCSDeviceServer',
                          r'Datasets\DCSDataSets.exe': 'DCSDataSets', 'DCSTestSchedule.exe': 'DCSTestSchedule'}

        xml_file = open(config_xml)
        parse_tree = et.parse(xml_file)
        root_node = parse_tree.getroot()
        for service_name in service_name_list:
            new_node = et.SubElement(root_node.find('servers'), attr_name)

            new_node.set('name', '{0}'.format(name_swap_dict[service_name]))
            new_node.set('path', os.path.join(process_path, service_name))

            new_node.set('otherArgs', '')
            new_node.set('isModule', '1')
            if 'DCSSoundCard' in service_name:
                new_node.set('testPort', '{0}'.format(math.ceil(test_port/2)))
            else:
                new_node.set('testPort', '{0}'.format(test_port))
            new_node.set('isAutoStart', '0')

        parse_tree.write(config_xml)


class WebSocket:
    def __init__(self, host_port):
        self.ws = None
        self.websocket_host_port = host_port

    def connect(self):
        self.ws = websocket.create_connection(self.websocket_host_port)
        return self.ws.getstatus()

    def send(self, send_data):
        self.ws.send(send_data)

    def send_get_res(self, send_data):
        self.ws.send(send_data)
        return self.ws.recv()

    def disconnect(self):
        self.ws.close()


class FTPHelper:
    def __init__(self, ftp_host='172.16.23.142', ftp_port=21, ftp_user='dcsman', ftp_pass='dingli123'):
        self.ftp = FTP()
        self.ftp_host = ftp_host
        self.ftp_port = ftp_port
        self.ftp_user = ftp_user
        self.ftp_pass = ftp_pass

    def _connect(self):
        self.ftp.connect(self.ftp_host, self.ftp_port)

    def _login(self):
        self.ftp.login(self.ftp_user, self.ftp_pass)

    def ftp_download(self, remote_path, local_path):
        """
        :param remote_path: ftp远端服务器文件绝对路径
        :param local_path: 本地路径
        """
        self._connect()
        self._login()
        # 切换到远程目录
        self.ftp.cwd(os.path.dirname(remote_path))
        # 下载文件
        with open(local_path, 'wb') as f:
            self.ftp.retrbinary('RETR ' + os.path.basename(remote_path), f.write)
        # 关闭 FTP 连接
        self.ftp.quit()

    def ftp_download_pattern(self, remote_path, local_path):
        """
        :param remote_path: ftp远端服务器文件绝对路径
        :param local_path: 本地路径
        """
        self._connect()
        self._login()
        # 切换到远程目录
        self.ftp.cwd(os.path.dirname(remote_path))

        # 获取目录中匹配通配符的文件列表
        print('remote_path: ', remote_path)
        print('local_path: ', local_path)
        if 'dcs_build' in remote_path:
            file_dcs = self.ftp.nlst(remote_path)
            print('file_dcs: ', file_dcs)
            local_path = os.path.join(os.path.dirname(local_path), file_dcs[0].replace('/', ''))
            remote_path = file_dcs[0]
        print('local_path: ', local_path)
        # 下载文件
        with open(local_path, 'wb') as f:
            self.ftp.retrbinary('RETR ' + os.path.basename(remote_path), f.write)
        # 关闭 FTP 连接
        self.ftp.quit()
        return local_path
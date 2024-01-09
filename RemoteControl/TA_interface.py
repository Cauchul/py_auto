# -*- coding:utf-8 -*-
import time
import json
import logging
import socket

import allure
from pytest_check import check

server_address = ('127.0.0.1', 30999)
print('socket 连接ip:{} 端口：{}'.format(*server_address))
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def send_cmd_get_res_no_allure(send_cmd, params=None, index=None, timeout=None):
    msg = {"CMD": send_cmd}
    if params:
        msg['Param'] = params
    if index is not None:
        msg['EQIndex'] = index
    msg = json.dumps(msg)
    msg = msg.encode('utf-8')
    print('发送命令：', msg)
    send_time = time.time()
    sock.send(msg)
    if timeout is None:
        sock.settimeout(60)
    else:
        sock.settimeout(timeout)
    data = sock.recv(1024 * 10)
    rec_time = time.time()
    response_time = rec_time - send_time
    print('命令：{0}，发送时间：{1}'.format(send_cmd, send_time))
    print('命令：{0}, 接收时间：{1}'.format(send_cmd, rec_time))
    print('命令：{0}, 响应时间为：{1}'.format(send_cmd, response_time))
    print('命令：{0}, 返回值为：{1}'.format(send_cmd, data))
    if data == b'':
        with check.check:
            with allure.step('命令：{0}，socket 返回值，期望值：值不为空，实际值：{1}'.format(send_cmd, data)):
                assert False
    else:
        # with check.check:
        #     with allure.step('命令：{0}，状态码，期望值：0，实际值：{1}'.format(send_cmd, json.loads(data)['Param']['State'])):
        #         assert 0 == json.loads(data)['Param']['State']
        return json.loads(data)


def send_cmd_to_ui(send_cmd, params=None, index=None, timeout=None):
    msg = {"CMD": send_cmd}
    if params:
        print('params: ', params)
        msg['Param'] = params
    if index is not None:
        msg['EQIndex'] = index
    msg = json.dumps(msg)
    msg = msg.encode('utf-8')
    with allure.step('发送命令：{0}'.format(msg)):
        print('发送命令：', msg)
    send_time = time.time()
    sock.send(msg)
    if timeout is None:
        sock.settimeout(180)
    else:
        sock.settimeout(timeout)
    data = sock.recv(1024 * 10)
    rec_time = time.time()
    response_time = rec_time - send_time
    with allure.step('命令：{0}，发送时间：{1}'.format(send_cmd, send_time)):
        print('命令：{0}，发送时间：{1}'.format(send_cmd, send_time))
    with allure.step('命令：{0}, 接收时间：{1}'.format(send_cmd, rec_time)):
        print('命令：{0}, 接收时间：{1}'.format(send_cmd, rec_time))
    with allure.step('命令：{0}, 响应时间为：{1}'.format(send_cmd, response_time)):
        print('命令：{0}, 响应时间为：{1}'.format(send_cmd, response_time))
    with allure.step('命令{0},返回值为：{1}'.format(send_cmd, data)):
        print('命令：{0}, 返回值为：{1}'.format(send_cmd, data))
    if data == b'':
        with check.check:
            with allure.step('命令：{0}，socket 返回值，期望值：值不为空，实际值：{1}'.format(send_cmd, data)):
                assert False
    else:
        with check.check:
            with allure.step('命令：{0}，状态码，期望值：0，实际值：{1}'.format(send_cmd, json.loads(data)['Param']['State'])):
                assert 0 == json.loads(data)['Param']['State']
        return json.loads(data), response_time, msg


def send_cmd_get_res(send_cmd, params=None, index=None, timeout=None):
    msg = {"CMD": send_cmd}
    if params:
        msg['Param'] = params
    if index is not None:
        msg['EQIndex'] = index
    msg = json.dumps(msg)
    msg = msg.encode('utf-8')
    with allure.step('发送命令：{0}'.format(msg)):
        print('发送命令：', msg)
    send_time = time.time()
    sock.send(msg)
    if timeout is None:
        sock.settimeout(180)
    else:
        sock.settimeout(timeout)
    data = sock.recv(1024 * 10)
    rec_time = time.time()
    response_time = rec_time - send_time
    with allure.step('命令：{0}，发送时间：{1}'.format(send_cmd, send_time)):
        print('命令：{0}，发送时间：{1}'.format(send_cmd, send_time))
    with allure.step('命令：{0}, 接收时间：{1}'.format(send_cmd, rec_time)):
        print('命令：{0}, 接收时间：{1}'.format(send_cmd, rec_time))
    with allure.step('命令：{0}, 响应时间为：{1}'.format(send_cmd, response_time)):
        print('命令：{0}, 响应时间为：{1}'.format(send_cmd, response_time))
    with allure.step('命令{0},返回值为：{1}'.format(send_cmd, data)):
        print('命令：{0}, 返回值为：{1}'.format(send_cmd, data))
    if data == b'':
        with check.check:
            with allure.step('命令：{0}，socket 返回值，期望值：值不为空，实际值：{1}'.format(send_cmd, data)):
                assert False
    else:
        with check.check:
            with allure.step('命令：{0}，状态码，期望值：0，实际值：{1}'.format(send_cmd, json.loads(data)['Param']['State'])):
                assert 0 == json.loads(data)['Param']['State']
        return json.loads(data)


def connect_socket():
    sock.connect(server_address)


def close_socket_conn():
    if sock is not None:
        sock.close()


# 扫描设备
def auto_check():
    cmd = 'AutoCheck'
    res = send_cmd_get_res_no_allure(cmd)
    print('AutoCheck 返回值为：', res)
    return res
    # return res['Param']['WorkingIndex']


# 连接设备
def connect_devices(writer):
    cmd = 'ConnectEQ'
    res, response_time, msg = send_cmd_to_ui(cmd)
    writer.writerow(list([None, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值为：', res)
    # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    if res['Param']['State'] == 0:
        print('连接设备 success')
    else:
        print("连接设备 failed")
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']
# def connect_devices():
#     res = send_cmd_to_ui("ConnectEQ")
#     print('命令返回值为：', res)
#     if res['Param']['State'] == 0:
#         print('连接设备 success')
#     else:
#         print("连接设备 failed")
#     return 'ConnectEQ', res['Param']['State']


# 断开设备
def disconnect_devices(writer, ue_index):
    cmd = 'DisConnectEQ'
    res, response_time, msg = send_cmd_to_ui(cmd)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值为：', res)
    if res['Param']['State'] == 0:
        print('设备断开 success')
    else:
        print("设备断开 failed")
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']
    # res = send_cmd_get_res("DisConnectEQ")
    # print('命令返回值为：', res)
    # if res['Param']['State'] == 0:
    #     print('设备断开 success')
    # else:
    #     print("设备断开 failed")
    # return 'DisConnectEQ', res['Param']['State']


# 开始记录
def start_log(writer):
    cmd = 'StartLog'
    res, response_time, msg = send_cmd_to_ui(cmd,
                           params={"LogPath": r"D:\auto_test_tmp_path", "LogName": "auto_test_log_filename"})
    writer.writerow(list([None, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值为：', res)
    if res['Param']['State'] == 0:
        print('开始记录成功, 返回状态为: {}'.format(res['Param']['State']))
    else:
        print('开始记录失败,返回状态为: {}'.format(res['Param']['State']))
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


# 停止记录
def stop_log(writer):
    cmd = 'StopLog'
    res, response_time, msg = send_cmd_to_ui(cmd)
    writer.writerow(list([None, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值为：', res)
    if res['Param']['State'] == 0:
        print('停止记录，成功')
    else:
        print('停止记录，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


# 物理上电
def physical_power_on(writer, ue_index=1):
    cmd = 'PhysicalPowerOn'
    param = {"WaitForOper": True}  # Wait the ue online

    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('上电，成功')
    else:
        print('上电，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


# 物理下电
def physical_power_off(writer, ue_index=1):
    cmd = 'PhysicalPowerOff'
    param = {
        "State": 0,  # return 0 if success, return -1 if failure or abnormal.
        "IsOffLine": 0  # return 0 if success, return -1 if it isn't offline.
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('下电，成功')
    else:
        print('下电，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


# 网络attach
def ue_attach(writer, ue_index=-1):
    cmd = 'Attach'
    param = {"UEMode": "5G_SA"}  # ”4G”or”5G_SA”or”5G_NSA”
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('attach，成功')
    else:
        print('attach，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


# 网络detach
def ue_detach(writer, ue_index=-1):
    cmd = 'Detach'
    param = {
        "WithPDU": 0  # 0 means without PDU, 1 means with PDU.
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('Detach，成功')
    else:
        print('Detach，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


# 发送cfun=1
def power_on(writer, ue_index=-1):
    cmd = 'PowerOn'
    res, response_time, msg = send_cmd_to_ui(cmd, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('power_on，成功')
    else:
        print('power_on，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


# 发送cfun=0
def power_off(writer, ue_index=-1):
    cmd = 'PowerOff'
    res, response_time, msg = send_cmd_to_ui(cmd, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('power_off，成功')
    else:
        print('power_off，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def send_at_command(at_cmd, writer, ue_index=1):
    cmd = 'SendAT'
    param = {
        "Command": at_cmd,  # AT command name
        "Timeout": 5000  # timeout, milliseconds
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('send_at_command，成功')
    else:
        print('send_at_command，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def start_test_plan(writer, ue_index=1):
    cmd = 'StartTest'
    res, response_time, msg = send_cmd_to_ui(cmd, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('start_test_plan，成功')
    else:
        print('start_test_plan，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def stop_test_plan(writer, ue_index=-1):
    cmd = 'StopTest'
    res, response_time, msg = send_cmd_to_ui(cmd, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('stop_test_plan，成功')
    else:
        print('stop_test_plan，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def start_traffic(writer, ue_index=-1):
    cmd = 'StartTraffic'
    param = {
        "Protocol": "UDP",  # {UDP/TCP},means default protocol UDP.
        "Address": "10.20.6.200",  # APP server IP address.
        "Port": "1314",  # UNION[int, Char]，APP server port.
        "TestTime": "120",  # UNION[int, Char]，Test time.
        "Bandwidth": 1000,  # Kbps. Optional if Protocol is TCP.
        "BufferSize": 0,  # KB，0~2GB.Can be set 0 if Portocol is UDP.
        "PacketSize": 1400,  # Byte
        "IperfType": 0,  # 0:iperf2; 1:iperf3.Can be set 1 if Direction is 1.
        "Direction": 0,  # 0:UpLink; 1: DownLink.
        "ThreadCount": 5
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res:
        if res['Param']['State'] == 0:
            print('start_traffic，成功')
        else:
            print('start_traffic，失败')
            # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
        return cmd, res['Param']['State']


def start_ul_traffic(writer, ue_index=1):
    cmd = 'StartULtraffic'
    param = {
        "Protocol": "UDP",  # {UDP/TCP},means default protocol UDP.
        "Address": "10.57.163.34",  # APP server IP address.
        "Port": "5001",  # APP server port.
        "TestTime": "120",  # Test time.
        "Bandwidth": 1000,  # Kbps.
        "BufferSize": 1024,  # KB
        "PacketSize": 1400,  # Byte
        "IperfType": 0,  # 0:iperf2; 1:iperf3
        "Direction": 0,  # 0:UpLink; 1: DownLink
        "ThreadCount": 1
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('start_ul_traffic，成功')
    else:
        print('start_ul_traffic，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def start_call(writer, ue_index=-1):
    cmd = 'StartCall'
    param = {
        "Number": "10000",  # called number
        "ConnectTime": 15,  # connection time limit (s)
        "Duration": 30,  # Call duration(s)
        "LongCall": False,  # whether long call, true or False.
        "MO-MT": False,  # Optional param, whether combine MO with MT
        "CalledUE": 2  # Optional param,{1~n}, 1 means the first UE,2 means the second UE, and so forth
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('start_call，成功')
    else:
        print('start_call，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def start_mos(writer, ue_index=1):
    cmd = 'StartMOS'
    param = {
        "CallMode": 0,  # 0:”MO-MT”, 1:”MOC”, 2:”MTC”.
        "CalledUE": 2,  # {1~n}, 1 means the first UE, 2 means the second UE, and so forth.
        "CalledNum": "13800000000",  # Called phone number.
        "VideoCall": 0,  # 0:means No, 1: means Yes.
        "Duration": 180,  # The unit is seconds, 0 means long call.
        "TestCount": 1,  # Test Count, 0 means infinite test.
        "Algorithms": 2,  # 0:” PESQ NB”, 1:”POLQA NB”, 2:” POLQA SWB”, 3:” PESQ WB”.
        "POLQAVersion": 1,  # 0:”V1.1”, 1:” V2.4”.
        "MOSBoxType": 1,  # 0:”Multi MOS Box”, 1:”Single MOS Box”.
        "GroupNo": 0
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('start_mos，成功')
    else:
        print('start_mos，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def start_ftp_dl(writer, ue_index=-1):
    cmd = 'StartFTPDL'
    param = {
        "Host": "10.20.6.200",
        "Port": 21,
        "Username": "user",
        "Password": "123",
        "ModeType": 0,
        "SaveFile": False,  # Whether to save the data file when downloading.
        "HostDir": "/download/100MB",
        "LocalDir": r"D:\auto_test_tmp_path",
        "Duration": 300,  # download duration (s)
        "ThreadCount": 30,  # Number of download threads
        "FtpType": "FTP",  # Protocol type FTP: ftp server, SFTP: sftp server.
        "PSCall": True,  # download by time
        "Timeout": 1200
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res:
        if res['Param']['State'] == 0:
            print('start_ftp_dl，成功')
        else:
            print('start_ftp_dl，失败')
            # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
        return cmd, res['Param']['State']


def start_ftp_ul(writer, ue_index=-1):
    cmd = 'StartFTPUL'
    param = {
        "Host": "183.221.242.254",
        "Port": 21,
        "Username": "xxx",
        "Password": "xxx",
        "ModeType": 0,
        # 0 means passive access，1 means active access，2 means extended passive access，3 means extended active access，
        "HostDir": "/",  # Server file path.
        "Size": 100000,  # Upload file size (KB).
        "Duration": 300,  # download duration (s)
        "ThreadCount": 30,  # Number of download threads
        "FtpType": "FTP",  # Protocol type FTP: ftp server, SFTP: sftp server.
        "DeleteFile": False,  # Whether to delete the files uploaded to the FTP server each time.
        "PSCall": True,  # upload by time
        "Timeout": 1200
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('start_ftp_ul，成功')
    else:
        print('start_ftp_ul，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def start_ping(writer, ue_index=-1):
    cmd = 'StartPing'
    param = {
        "Host": "10.20.6.200",  # IP address.
        "PacketSize": 50,  # Ping packet size (Bytes).
        "LiveTime": 50,  # lifetime.
        "TimeOut": 1500,  # Timeout time (ms).
        "ATPing": False  # Whether to use AT command to test Ping (only for IoT module devices), True or False.
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res:
        if res['Param']['State'] == 0:
            print('StartPing，成功')
        else:
            print('StartPing，失败')
            # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
        return cmd, res['Param']['State']


# 执行多测测试计划
def start_composite_test_plan(writer, ue_index=1):
    cmd = 'StartCompositeTestPlan'
    param = [{
        "TestKind": "Iperf",
        "TestParam": {
            "Protocol": "UDP",  # {UDP/TCP},means default protocol UDP.
            "Address": "10.20.6.200",  # APP server IP address.
            "Port": "1314",  # UNION[int, Char]，APP server port.
            "TestTime": "1200",  # UNION[int, Char]，Test time.
            "Bandwidth": 204800,  # Kbps. Optional if Protocol is TCP.
            "BufferSize": 0,  # Byte
            "PacketSize": 1400,
            "IperfType": 0,  # 0:iperf2; 1:iperf3.Can be set 1 if Direction is 1.
            "Direction": 0,  # 0:UpLink; 1: DownLink.
            "ThreadCount": 5
        }
    },
        {
            "TestKind": "Iperf",
            "TestParam": {
                "Protocol": "UDP",  # {UDP/TCP},means default protocol UDP.
                "Address": "10.20.6.200",
                "Port": "1315",
                "TestTime": "1200",
                "Bandwidth": 204800,  # Kbps. Optional if Protocol is TCP.
                "BufferSize": 0,
                "PacketSize": 1400,
                "IperfType": 1,  # 1:iperf3. Default type is iperf3.
                "Direction": 1,  # 0:UpLink; 1: DownLink.
                "ThreadCount": 5
            }
        }
    ]
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res:
        if res['Param']['State'] == 0:
            print('StartCompositeTestPlan，成功')
        else:
            print('StartCompositeTestPlan，失败')
            # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
        return cmd, res['Param']['State']


def get_param_mac(writer, ue_index=1):
    cmd = 'GetParamMAC'
    res, response_time, msg = send_cmd_to_ui(cmd, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('GetParamMAC，成功')
    else:
        print('GetParamMAC，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def get_param_imsi(writer, ue_index=1):
    cmd = 'GetParamIMSI'
    res, response_time, msg = send_cmd_to_ui(cmd, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('GetParamIMSI，成功')
    else:
        print('GetParamIMSI，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def get_param_imei(writer, ue_index=1):
    cmd = 'GetParamIMEI'
    res, response_time, msg = send_cmd_to_ui(cmd, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('GetParamIMEI，成功')
    else:
        print('GetParamIMEI，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def get_param_ip(writer, ue_index=1):
    cmd = 'GetParamIP'
    param = {
        "PDUID": 1  # {1~n},pdu id index specified by PDU setup cmd.
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('GetParamIP，成功')
    else:
        print('GetParamIP，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def get_pdu_info(writer, ue_index=1):
    cmd = 'GetPDUInfo'
    param = {
        "APN ": "3gnet"  # PDU APN address.
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('GetPDUInfo，成功')
    else:
        print('GetPDUInfo，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def get_attach_status(writer, ue_index=1):
    cmd = 'GetAttachStatus'
    res, response_time, msg = send_cmd_to_ui(cmd, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('GetAttachStatus，成功')
    else:
        print('GetAttachStatus，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def start_statist_ics(writer, ue_index=1):
    cmd = 'StartStatistics'
    res, response_time, msg = send_cmd_to_ui(cmd, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('StartStatistics，成功')
    else:
        print('StartStatistics，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def stop_statist_ics(writer, ue_index=1):
    cmd = 'StopStatistics'
    res, response_time, msg = send_cmd_to_ui(cmd, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('StopStatistics，成功')
    else:
        print('StopStatistics，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def get_statistics_result(writer, ue_index=1):
    cmd = 'GetStatisticsResult'
    param = {
        "State": 0,
        "CQI": [{
            "Rage": "(-INF,3]",
            "Count": 0,
            "CDF": "0%",
            "PDF": "0%"
        },],
        "ULBler": [{
            "Rage": "(-INF,3]",
            "Count": 0,
            "CDF": "0%",
            "PDF": "0%"
        },],
        "DLBler": [{
            "Rage": "(-INF,3]",
            "Count": 0,
            "CDF": "0%",
            "PDF": "0%"
        },]
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('GetStatisticsResult，成功')
    else:
        print('GetStatisticsResult，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def get_param_statistics_result(writer, ue_index=1):
    cmd = 'GetParamStatisticsResult'
    param = {
        "State": 0,
        "SS-RSRP": [{
            "Rage": "(-INF,-110)",
            "Count": 0,
            "CDF": "0%",
            "PDF": "0%"
        },],
        "SS-SINR": [{
            "Rage": "(-INF,-3)",
            "Count": 0,
            "CDF": "0%",
            "PDF": "0%"
        },],
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('GetParamStatisticsResult，成功')
    else:
        print('GetParamStatisticsResult，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def get_event_statistics_result(writer, ue_index=1):
    cmd = 'GetEventStatisticsResult'
    param = {
        "State": 0, #return 0 if success, otherwise return the error codes.
        "Ping Request": 10,
        "Ping Success": 10,
        "Ping Failure": 0
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('GetEventStatisticsResult，成功')
    else:
        print('GetEventStatisticsResult，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def get_param_summary_statistics_result(writer, ue_index=1):
    cmd = 'GetParamSummaryStatisticsResult'
    param = {
        "ParamName": ["SS-RSRP", "SS-SINR"] #the name refer to the table window.
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('GetParamSummaryStatisticsResult，成功')
    else:
        print('GetParamSummaryStatisticsResult，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def loop_settings(writer, ue_index=-1):
    cmd = 'LoopSettings'
    param = {
        "Times": 1, #Cycle times
        "LoopInterval": 10, #Cycle interval
        "SerialInterval": 10  #Business interval
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('LoopSettings，成功')
    else:
        print('LoopSettings，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def config_5G_deployment(writer, ue_index=1):
    cmd = 'Config5GDeployment'
    param = {
        "NetType": 0 #0:"Autoselection", 8:"5GNSA", 20:"5GSA+5GNSA"
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('Config5GDeployment，成功')
    else:
        print('Config5GDeployment，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def setups_NSSAI(writer, ue_index=1):
    cmd = 'SetupS_NSSAI'
    param = {
        "ID": 1, #PDU ID, specified in PDU setup
        "Type": "IPV4V6", #IPV4,IPV6 or IPV4V6
        "APN": "3gnet",
        "SSC_mode": 0, #0 or 1
        "S_NSSAI": "1.123456;2F.654321" #HEX formatfor0-1 and A-F
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('SetupS_NSSAI，成功')
    else:
        print('SetupS_NSSAI，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def setup_PDU(writer, ue_index=1):
    cmd = 'SetupPDU'
    param = {
        "ID": 1, #PDU ID,specified in PDU setup
        "Type": "IPV4V6", #IPV4,IPV6 or IPV4V6
        "APN": "3gnet",
        "SSC_mode": 0, #Optional parm, if set, add this parm to AT command.
        "S_NSSAI": "" #Optional parm, if set, add this parm to AT command.
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('SetupPDU，成功')
    else:
        print('SetupPDU，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']


def configure_APN(writer, ue_index=1):
    cmd = 'ConfigureAPN'
    param = {
        "APNName": "wap1", #if apn name existed, update this apn, else insert apn.
        "APN": "3gnet", #APN address
        "MCC": "460", #MCC code
        "MNC": "02" #MNC code
    }
    res, response_time, msg = send_cmd_to_ui(cmd, param, index=ue_index)
    writer.writerow(list([ue_index, cmd, response_time, msg, res, res['Param']['State']]))
    print('命令返回值：', res)
    if res['Param']['State'] == 0:
        print('ConfigureAPN，成功')
    else:
        print('ConfigureAPN，失败')
        # writer.writerow(list([cmd, response_time, msg, res, res['Param']['State']]))
    return cmd, res['Param']['State']

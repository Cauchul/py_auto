# -*- coding:utf-8 -*-
import os
import subprocess
import sys
import time

import pytest
import allure
from pytest_check import check
sys.path.append("..")
# import Common.GobalVariabies

object_path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(object_path)

from Common.pip_install import *
pip_install_by_requirement_file(loop=1)

from Common.GobalVariabies import *
from Common.Operation import *


def check_process_exist_or_not(process_name):
    with check.check:
        if process_name:
            flag = True
            print('process_name: ', process_name)
            with allure.step('根据进程名称，判断进程是否存在'):
                for i in process_name:
                    if 'DCSPlay.exe' == i:
                        continue
                    state = check_process_is_exist(i)
                    print('state: ', state)
                    if state:
                        with allure.step('{0}服务的进程存在'.format(i)):
                            pass
                    else:
                        with allure.step('{0} 服务的进程不存在'.format(i)):
                            flag = False
                            assert state
                if flag:
                    with allure.step('DCS相关的服务的进程存在, 启动服务成功！'):
                        pass


def check_running_status(all_process_list):
    if all_process_list:
        flag = True
        with allure.step('检查redis中的DCSDaemon-process_list键值， 判断DCS相关服务的进程状态是否为：Running？'):
            for i in all_process_list:
                print('当前检查服务名称为：', i)
                with check.check:
                    if 'Running' != all_process_list[i]:
                        with allure.step('检查{0}服务的进程状态失败, 期望状态：Running, 实际状态：{1}.'.format(i, all_process_list[i])):
                            # 检查process_list状态
                            flag = False
                            assert 'Running' == all_process_list[i]
                    else:
                        with allure.step("检查{0}服务的进程状态成功, 期望状态：Running, 实际状态：{1}.".format(i, all_process_list[i])):
                            pass
            if flag:
                with allure.step('检查DCS相关服务在Redis 的状态成功'):
                    pass
            else:
                with allure.step("检查DCS相关服务在Redis 的状态失败, 本次测试失败. 退出测试"):
                    sys.exit("test exited")


def check_service_status(all_process_list):
    for service in all_process_list:
        server_status = f_redis.hget(service, 'server_status')
        print('service：', service)
        print('server_status：', server_status)
        if 'Servering' == server_status or 'servering' == server_status:
            pass
        else:
            with assume:
                if server_status:
                    with allure.step('错误，服务：{0} 状态检测错误，服务状态：{1}'.format(service, server_status)):
                        pass
                        # assert 'Servering' == server_status
                else:
                    with allure.step('错误，服务：{0} 状态检测错误，服务状态：{1}'.format(service, server_status)):
                        pass
                        # assert server_status


def check_process_status():
    # device_id = f_redis.hkeys('device_list')
    device_id = get_device_id_from_redis()
    process_list_hash = device_id + '-DCSDaemon-process_list'
    all_process_list = f_redis.hgetall(process_list_hash)
    print('device_id: ', device_id)
    print('all_process_list: ', all_process_list)

    if all_process_list:
        # 检查运行状态
        with allure.step('检查进程运行状态'):
            print('检查进程运行状态')
            check_running_status(all_process_list)
        # 检查服务状态
        with allure.step('检查进程服务状态'):
            print('检查进程服务状态')
            check_service_status(all_process_list)
    else:
        with check.check:
            with allure.step('失败，当前进程列表为：{0}'.format(all_process_list)):
                assert all_process_list


def ftp_down_load(ftp_down_file_list):
    tmp_list = []
    ftp = FTPHelper()
    for get_file in ftp_down_file_list:
        local_7z_path = os.path.join(local_tmp_path, os.path.basename(get_file))
        if os.path.exists(local_7z_path):
            os.system('rd /s/q {0}'.format(local_7z_path))
        ftp.ftp_download(get_file, local_7z_path)
        tmp_list.append(local_7z_path)
    return tmp_list


def unzip_file(file_list):
    depend_path = dcs_build_path = None
    for file in file_list:
        unzip_path = os.path.join(dcs_path, os.path.basename(file)[:os.path.basename(file).rfind('_')])
        print('unzip_path: ', unzip_path.split('\\')[-1])
        if 'DCSTests' in unzip_path.split('\\')[-1]:
            depend_path = unzip_path
        if 'dcs_build' in unzip_path.split('\\')[-1]:
            dcs_build_path = unzip_path
        os.system('rd /s/q {0}'.format(unzip_path))
        unzip_7z_file(file, unzip_path)
    return depend_path, dcs_build_path


# @pytest.fixture(scope="session", autouse=True)
def download_update_latest_package():
    # 清理环境
    clean_up_test_case_runtime_env()

    today = get_today_time()
    ftp_down_file_list = ['/DCSTests_bin.7z', '/dcs_build_{0}.7z'.format(today), '/pioneer_build_{0}.7z'.format(today),
                 '/uiservice_build_{0}.7z'.format(today)]

    download_file_list = ftp_down_load(ftp_down_file_list)
    print('download_file_list: ', download_file_list)

    dcs_tests_bin_path, dcs_build_path = unzip_file(download_file_list)
    print('dcs_tests_bin_path: ', dcs_tests_bin_path)
    print('dcs_build_path: ', dcs_build_path)

    # 拷贝依赖文件
    src_path = os.path.join(dcs_tests_bin_path, 'DCSTests_bin')
    des_path = os.path.join(dcs_build_path, 'bin')
    for src_dir in os.listdir(src_path):
        print('当前拷贝的 DCS 依赖文件为：', src_path)
        print('目的路径：', des_path)
        copy_file(os.path.join(src_path, src_dir), os.path.join(des_path, src_dir))
    os.system('rd /s/q {0}'.format(dcs_tests_bin_path))

    # 拷贝最新的dll和exe到数据集目录下
    copy_list = ['DCSPlay.exe', 'DCSPlayDll.dll', 'DCSDataSets.exe', 'DCSDataSetsDll.dll']
    for file in copy_list:
        copy_file_path = os.path.join(des_path, file)
        print('拷贝到数据集的文件为：', copy_file_path)
        copy_file(copy_file_path, os.path.join(des_path, 'Datasets'))


@pytest.fixture(scope="session", autouse=True)
def ta_prepare_test():
    with allure.step("准备测试环境和测试前置条件:"):
        with allure.step('拷贝证书文件'):
            copy_file(os.path.join(xml_path, 'DingLiCA.pem'), local_tmp_path)
            copy_file(os.path.join(xml_path, 'PFS.p12'), local_tmp_path)
        with allure.step('启动日志服务'):
            script_file_name = os.path.join(local_tmp_path, 'start_logger_service.bat')
            run_cmd = '{0} & cd {1} & start logger_server.exe & exit'.format(cur_drive, exe_path)
            with open(script_file_name, 'w') as fh:
                fh.write(run_cmd)
            cmd = r'start {0}'.format(script_file_name)
            with allure.step('start LoggerService with cmd: {0}'.format(cmd)):
                print('cmd：', cmd)
                os.system(cmd)
                time.sleep(1)
                if check_process_is_exist('logger_server.exe'):
                    with allure.step('日志服务启动成功'):
                        pass
                else:
                    os.remove(script_file_name)
                    exit('日志服务启动失败')
                os.remove(script_file_name)

        with allure.step('启动DCS相关的所有服务'):
            with allure.step('启动DCSDaemon相关服务'):
                print('启动DCSDaemon相关服务: ', exe_path)
                start_service(exe_path, config_xml_path)
                time.sleep(3)
            with allure.step('检测DCS相关服务的进程状态'):
                check_process_exist_or_not(process_name_list)
                # print('等待 20s 检测服务状态......')
                # time.sleep(20)
                # check_process_status()
            with allure.step('启动UIService'):
                print('启动UIService')
                start_ui_cmd = r'{0} && cd {1} && DCSUIService.exe'.format(cur_drive, os.path.join(dcs_path,
                                                                                                   r'uiservice_build\Output'))
                with allure.step('执行 UIService 启动命令: {0}'.format(start_ui_cmd)):
                    print('执行 UIService 启动命令: {0}'.format(start_ui_cmd))
                    run_bat_cmd_start_thread(start_ui_cmd)
                # time.sleep(2)
    yield
    with allure.step("清除测试环境及测试数据:"):
        print('==' * 50)
        with allure.step('清理启动的所有服务'):
            process_name_list.append('DCSUIService.exe')
            if process_name_list:
                for process_name in process_name_list:
                    clear_cmd = 'taskkill /F /im {0}'.format(process_name)
                    print('clear_cmd: ', clear_cmd)
                    os.system(clear_cmd)

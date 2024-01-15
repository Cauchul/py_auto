# -*- coding:utf-8 -*-
import datetime
import errno
import os
import random
import shutil
import sys
import time

import allure
import pytest

from pytest_check import check
from datetime import datetime, timedelta

import Common.GobalVariabies
from Common.GobalVariabies import *
from Common.Operation import parse_xml_get_test_port_list


@allure.feature('DCS系统管理测试')
class TestDCSSystemMgr:
    def setup_class(self):
        log_path = os.path.join(exe_path, 'log')
        log_name = str(datetime.now().strftime('%m-%d')) + '.log'
        TestDCSSystemMgr.log_name_path = os.path.join(log_path, log_name)
        print('log_name_path: ', TestDCSSystemMgr.log_name_path)
        # 等待日志对齐
        time.sleep(60)

    # @pytest.mark.skip(reason="需要等待 10min，每个新版本测试一次")
    @allure.step('系统监控')
    def test_disk_space_monitor(self):
        root_node = ParseXml.get_root_by_xml_name(config_xml_path)
        data_out_dir = root_node.find('common/data_out_dir').get('dir')
        source_file = os.path.join(test_data_path, 'systemMgr_test_check_file.qmdl')
        dump_path = os.path.join(data_out_dir, r'DCSSoundMgr\RecordFileTmp')
        old_time_des_file = os.path.join(dump_path, 'systemMgr_test_check_file_old_time.qmdl')
        new_time_des_file = os.path.join(dump_path, 'systemMgr_test_check_file_new_time.qmdl')
        print('dump_path: ', dump_path)
        with allure.step('拷贝检测文件到dump目录下'):
            with allure.step('拷贝 {0} 文件'.format(old_time_des_file)):
                shutil.copy2(source_file, old_time_des_file)
            with allure.step('拷贝 {0} 文件'.format(new_time_des_file)):
                shutil.copyfile(source_file, new_time_des_file)

        drive = exe_path.split('\\')[0]

        with allure.step('写满磁盘到百分之85之上'):
            i = 0
            last_disk_usage = 0
            while True:
                if psutil.disk_usage(drive).percent > 85 or last_disk_usage > psutil.disk_usage(drive).percent:
                    with allure.step('当前的磁盘：{0}，的磁盘占用率为：{1}'.format(drive, psutil.disk_usage(drive).percent)):
                        break
                last_disk_usage = psutil.disk_usage(drive).percent
                huge_filename = os.path.join(dump_path, 'hugefile_{0}.txt'.format(i))
                with open(huge_filename, 'wb') as f:
                    f.seek(1024 * 1024 * 1024)
                    f.write(b'\0')

                print('cur_i: ', i)
                print('cur_disk_usage: ', psutil.disk_usage(drive).percent)
                i = i + 1

        with allure.step('等待 60s，磁盘使用超过85%，等待系统管理每分钟巡查、清理dump文件'):
            print('sleep 600s 等待，系统管理清理多余文件')
            time.sleep(600)
        # 检查文件是否存在
        with allure.step('系统管理服务，清理完毕后后，检测断言文件'):
            with allure.step('测试文件 {0} 是否删除，期望值：True，实际值：{1}'.format(old_time_des_file, not os.path.exists(old_time_des_file))):
                assert not os.path.exists(old_time_des_file)
            with allure.step('测试文件 {0} 是否存在，期望值：True，实际值：{1}'.format(new_time_des_file, os.path.exists(new_time_des_file))):
                assert os.path.exists(new_time_des_file)

        # 清理加压文件
        for root, dirs, files in os.walk(dump_path):
            print('files: ', files)
            # 清理 check 文件
            check_new_time_name = 'systemMgr_test_check_file_new_time.qmdl'
            os.remove(os.path.join(root, check_new_time_name))
            for name in files:
                if 'hugefile' in name:
                    print('name: ', name)
                    os.remove(os.path.join(root, name))

    @allure.step('数据库监控测试')
    def test_database_monitor(self):
        cur_start_test_time = datetime.now()
        # 获取当前时间月份减1的时间
        if cur_start_test_time.month > 1:
            cur_date_year = cur_start_test_time.year
            cur_date_month = cur_start_test_time.month - 1
        else:
            cur_date_month = 12
            cur_date_year = cur_start_test_time.year - 1

        try:
            last_month = datetime(cur_date_year, cur_date_month, cur_start_test_time.day, cur_start_test_time.hour,
                                  cur_start_test_time.minute, cur_start_test_time.second, cur_start_test_time.microsecond)
        except ValueError:
            last_month = datetime(cur_date_year, cur_date_month, cur_start_test_time.day - 1, cur_start_test_time.hour,
                                  cur_start_test_time.minute, cur_start_test_time.second,
                                  cur_start_test_time.microsecond)
        print('last_month: ', last_month)

        # 获取前一天的时间,设置五分钟的误差值
        last_day = cur_start_test_time - timedelta(days=1, minutes=25)
        print('last_day: ', last_day)

        # 获取当前时间12个小时前的时间
        last_hour = cur_start_test_time - timedelta(hours=12, minutes=5)
        print('last_hour: ', last_hour)

        with allure.step('检查数据库， source_file_de 表'):
            pg_select_cmd = 'SELECT * FROM "public"."source_file_def" ORDER BY "source_file_def"."create_dt" LIMIT 1'
            res_data = pg_project.pg_run_sql_fetchall(pg_select_cmd)[0]
            print('source_file_de_res_data: ', res_data)
            with check.check:
                with allure.step(
                        'source_file_de 只保留一个月内的数据，当前时间：{0}，界限时间： {1}，读取的最远的时间：{2}'.format(cur_start_test_time, last_month,
                                                                                           res_data[6])):
                    print('source_file_de_res_data: ', res_data[6])
                    print('type last_month: ', type(last_month))
                    assert res_data[6] >= last_month

        with allure.step('检查数据库， device_event_def 表'):
            pg_select_cmd = 'SELECT * FROM "public"."device_event_def" ORDER BY "device_event_def"."record_datetime" LIMIT 1'
            res_data = pg_project.pg_run_sql_fetchall(pg_select_cmd)[0]
            print('device_event_def_res_data: ', res_data)
            with check.check:
                with allure.step(
                        'device_event_def 只保留一天内的数据，当前时间：{0}，界限时间： {1}，读取的最远的时间：{2}'.format(cur_start_test_time, last_day,
                                                                                            res_data[11])):
                    print('device_event_def_res_data: ', res_data[11])
                    print('type last_day: ', type(last_day))
                    assert res_data[11] >= last_day

        with allure.step('检查数据库， process_info_def 表'):
            pg_select_cmd = 'SELECT * FROM "public"."process_info_def" ORDER BY "process_info_def"."create_time" LIMIT 1'
            res_data = pg_project.pg_run_sql_fetchall(pg_select_cmd)[0]
            print('process_info_def_res_data: ', res_data)
            with check.check:
                with allure.step(
                        'process_info_def 只保留一天内的数据，当前时间：{0}，界限时间： {1}，读取的最远的时间：{2}'.format(cur_start_test_time, last_day,
                                                                                              res_data[7])):
                    print('process_info_def_res_data: ', res_data[7])
                    print('type last_day: ', type(last_day))
                    assert res_data[7] >= last_day

        with allure.step('检查数据库， system_info_def 表'):
            pg_select_cmd = 'SELECT * FROM "public"."system_info_def" ORDER BY "system_info_def"."create_time" LIMIT 1'
            res_data = pg_project.pg_run_sql_fetchall(pg_select_cmd)[0]
            with check.check:
                with allure.step(
                        'system_info_def 只保留一天内的数据，当前时间：{0}，界限时间： {1}，读取的最远的时间：{2}'.format(cur_start_test_time, last_day,
                                                                                             res_data[5])):
                    print('res_data: ', res_data[5])
                    assert res_data[5] >= last_day

        with allure.step('检查数据库， disk_info_def 表'):
            pg_select_cmd = 'SELECT * FROM "public"."disk_info_def" ORDER BY "disk_info_def"."create_time" LIMIT 1'
            res_data = pg_project.pg_run_sql_fetchall(pg_select_cmd)[0]
            with check.check:
                with allure.step(
                        'disk_info_def 只保留一天内的数据，当前时间：{0}，界限时间： {1}，读取的最远的时间：{2}'.format(cur_start_test_time, last_day,
                                                                                           res_data[5])):
                    print('res_data: ', res_data[5])
                    assert res_data[5] >= last_day

    @allure.step('进程监控测试')
    def test_process_monitor(self):
        process_flag = True
        for line in reversed(list(open(TestDCSSystemMgr.log_name_path, 'rb'))):
            if not process_flag:
                print('-----------ProcessMonitor END----------')
                break
            if b'ProcessMonitor.cpp' in line.rstrip() and b'system cpu' in line.rstrip() and process_flag:
                process_flag = False
                # python获取当前cpu
                cur_cpu_use = psutil.cpu_percent()
                print("CPU使用率：", cur_cpu_use)
                # 获取日志中的cpu占用
                process_log_cpu = line.rstrip().decode('ascii').split(' ')[-1].split(':')[-1].split('%')[0]
                print('=== process_log_cpu: ', process_log_cpu)
                log_cpu_use = float(format(float(process_log_cpu), '.1f'))
                print('=== type: ', log_cpu_use)
                with allure.step('系统 CPU 总使用率检测'):
                    with check.check:
                        with allure.step('当前系统， CPU 总使用率为：{0}，系统管理获取到的 CPU 总使用率为：{1}，期望误差：6以内，实际误差：{2}'.format(cur_cpu_use, log_cpu_use, abs(log_cpu_use-cur_cpu_use))):
                            assert abs(log_cpu_use-cur_cpu_use) < 6

                # 获取当前时间
                current_date = datetime.now().strftime('%m-%d %H:%M:%S')
                print('current_date: ', current_date)
                print('line.rstrip：', line.rstrip())
                # 获取日志时间
                process_log_time = line.rstrip().decode('ascii').split(' ')[4] + ' ' + \
                                   line.rstrip().decode('ascii').split(' ')[5]
                print('process_log_time: ', process_log_time)
                with allure.step('进程监控，每分钟更新监控信息到日志文件'):
                    with check.check:
                        deal_current_date = datetime.strptime(current_date, '%m-%d %H:%M:%S')
                        deal_process_log_time = datetime.strptime(process_log_time.split(".")[0], '%m-%d %H:%M:%S')
                        with allure.step('当前时间：{0}，上条日志写入时间：{1}，期望误差值：65s内，实际误差值：{2}'.format(current_date, process_log_time, (deal_current_date - deal_process_log_time).seconds)):
                            assert (deal_current_date - deal_process_log_time).seconds < 65
        # time.sleep(120)
        with allure.step('进程CPU使用率和内存使用率检测'):
            print('process_name_list:', process_name_list)
            for process_name in process_name_list:
                if 'DCSPlay.exe' in process_name:
                    continue
                get_pg_data_sql = 'select "process_info_def"."process_cpu_usage","process_info_def"."process_physical_memory" ' \
                                  'from "public"."process_info_def" WHERE "process_info_def"."process_name" = \'{0}\' ORDER BY "process_info_def"."create_time" DESC LIMIT 1'.format(process_name)
                log_process_data = pg_project.pg_run_sql_fetchone(get_pg_data_sql)
                if log_process_data is not None:
                    # python 获取进程的信息
                    cur_process_data = get_cpu_and_memory_usage(process_name)
                    print('log_process_data data: {0}'.format(log_process_data))
                    print("cur_process_data data: {0}".format(cur_process_data))
                    cur_get_cpu = cur_process_data[2]
                    log_get_cpu = float(log_process_data[0].split('%')[0])
                    cur_get_mem = float(cur_process_data[-1])
                    log_get_mem = float(log_process_data[1].split('M')[0])
                    with allure.step('当前检测进程为：{0}'.format(process_name)):
                        with check.check:
                            with allure.step('获取的当前 CPU 占用率：{0}，系统管理服务获取到的 CPU 占用率：{1}，期望误差值：2以内，实际误差值：{2}'.format(cur_get_cpu, log_get_cpu, abs(cur_get_cpu-log_get_cpu))):
                                assert abs(cur_get_cpu-log_get_cpu) < 2
                            if 'DCSDataSets.exe' in process_name:
                                with allure.step(
                                        '获取的当前，内存使用大小：{0}，系统管理服务获取到的内存使用大小：{1}，期望误差值：70以内，实际误差值：{2}'.format(
                                                cur_get_mem, log_get_mem, abs(cur_get_mem - log_get_mem))):
                                    assert abs(cur_get_mem - log_get_mem) < 80
                            else:
                                with allure.step('获取的当前，内存使用大小：{0}，系统管理服务获取到的内存使用大小：{1}，期望误差值：22以内，实际误差值：{2}'.format(cur_get_mem, log_get_mem, abs(cur_get_mem - log_get_mem))):
                                    assert abs(cur_get_mem - log_get_mem) < 22
                else:
                    with check.check:
                        with allure.step('Failed，PG表 process_info_def 中，进程 {0} 的进程信息为：{1}'.format(process_name, log_process_data)):
                            assert log_process_data


if __name__ == "__main__":
    TestDCSSystemMgr().test_MemoryMonitor()

from pytest_check import check

from Common.DataFactory import *
from Common.Operation import *
from Common.pip_install import *

import csv
import datetime
import gc
import logging
import os
import threading
import pytest
import time
import allure
import psutil
from pynng import nng
from pytest_assume.plugin import assume
from Common.GobalVariabies import *

NANOMSG_PUSH_INTERFACE = 'tcp://127.0.0.1:8860'

if not os.path.exists(os.path.join(PROJECT_TESTCASE_DIR, 'logger_server_test_data')):
    os.makedirs(os.path.join(PROJECT_TESTCASE_DIR, 'logger_server_test_data'))

formatter = logging.Formatter('%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler(CIRCULAR_LOG_NAME)
console = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(console)


@allure.feature("日志服务测试")
class TestLoggerService:
    def setup_class(self):
        with allure.step('生成测试数据'):
            print("---start create_data---")
            DataCenter.FlyData.generate_size_32k_file()
            TestLoggerService.log_path = os.path.join(get_path_by_process_name('logger_server.exe'), 'log')
            print('log_path: ', TestLoggerService.log_path)

    def teardown_class(self):
        pass

    @allure.step("断言端口是否产生对应日志文件")
    def assert_port_and_log_file(self, data_fake_dict):
        print('---assert_port_and_log_file---')
        today = datetime.today().date()
        for port in data_fake_dict:
            if port < 2147483648:
                file_name = str(today).split('-')[1] + '-' + str(today).split('-')[2] + '-' + 'p' + str(port) + '.log'
            else:
                file_name = str(today).split('-')[1] + '-' + str(today).split('-')[2] + '.log'
            self.assert_log_content(file_name, port, data_fake_dict)

    @allure.step("断言日志内容是否正确写入日志文件")
    def assert_log_content(self, file_name, lot_port, data_fake_dict):
        absolute_path_name = os.path.join(TestLoggerService.log_path, file_name)
        if os.path.exists(absolute_path_name):
            with open(absolute_path_name, 'r', encoding='utf-8', errors='ignore') as fh:
                offset = 1024 * 36
                fh.seek(0, os.SEEK_END)
                file_size = fh.tell()
                buf_size = min(file_size, offset)
                fh.seek(file_size - buf_size)
                log_lines = fh.readlines()
                fh.close()
                count = 0
                for data in data_fake_dict[lot_port]:
                    count += 1
                    flag = True
                    for line in log_lines:
                        # if line.strip() == (str(lot_port) + data).strip():
                        if data.strip() in line.strip():
                            flag = False
                    if flag:
                        try:
                            with assume:
                                with allure.step("发送的日志数据：{0}，未在日志文件：{1}中找到".format(data, file_name)):
                                    assert 1 == 0
                        except AssertionError:
                            print("发送的日志数据：{0}，未在日志文件：{1}中找到".format(data, file_name))
                    else:
                        with allure.step("端口{0}的第{1}个数据，发送的和接收的数据一致".format(lot_port, count)):
                            pass
                del log_lines
                gc.collect()
        else:
            with assume:
                with allure.step("文件：{0}不存在".format(absolute_path_name)):
                    assert 1 == 0

    # @allure.step("start_push")
    def start_push_log_data(self, data, push_host_port):
        push_sock = nng.Push0(dial=push_host_port)
        push_flag = True
        try:
            push_sock.send(data.encode())
            with allure.step('push_data:{0}'.format(data)):
                print('push_data:{0}'.format(data))
            time.sleep(0.3)
        except:
            with allure.step('push_data, error'):
                push_flag = False
                print('push_data, error')
        if push_flag:
            with allure.step('push_data success'):
                pass
        push_sock.close()

    def middle_night_assert_file(self, date):
        logger.info('---middle_night_assert_file---')
        for port in range(1, 101):
            file_name = str(date).split('-')[1] + '-' + str(date).split('-')[2] + '-' + 'p' + str(port) + '.log'
            path_and_name = os.path.join(TestLoggerService.log_path, file_name)
            if not os.path.exists(path_and_name):
                logger.info('{0}的日志文件{1}不存在'.format(date, file_name))

    def write_mem_usage_data_to_csv_file(self, csv_file_name, data):
        fh = open(csv_file_name, "a", newline='')
        writer = csv.writer(fh)
        writer.writerow(data)
        fh.close()
        del writer

    def write_usage_data_to_csv(self):
        print('---write_usage_data_to_csv---')
        fh = open(MULTITHREADING_CIRCULAR_LOGGER_SERVER_SYSTEM_DATA, "w", newline='')
        writer = csv.writer(fh)
        header = ['task_end_time', '系统单核CPU使用率', 'logger_server进程CPU使用率', 'available memory',
                  'Memory Used by logger_server']
        writer.writerow(header)
        fh.close()
        del writer
        while True:
            usage_data = get_cpu_and_memory_usage('logger_server.exe')
            logger.info('usage_data: {0}'.format(usage_data))
            self.write_mem_usage_data_to_csv_file(MULTITHREADING_CIRCULAR_LOGGER_SERVER_SYSTEM_DATA, usage_data)
            time.sleep(88)

    def thread_normal_data_test(self):
        thread_list = []
        normal_data_fake_dict = DataCenter.FlyData.random_port_and_content()
        for i in range(30):
            t = threading.Thread(target=self.while_true_normal_data_test, args=(normal_data_fake_dict,))
            t.start()
            thread_list.append(t)
        thread_write_data = threading.Thread(target=self.write_usage_data_to_csv)
        thread_write_data.setDaemon = True
        thread_write_data.start()
        for i in thread_list:
            i.join()
        print('pressure test multithreading')

    def while_true_normal_data_test(self, normal_data_fake_dict):
        print('---multithreading_circular_test_normal_logger_data---')
        today = datetime.today().date()
        num = 0
        while True:
            num += 1
            logger.info('第{0}次运行'.format(num))
            cont = 0
            for port in normal_data_fake_dict:
                for fake_data in normal_data_fake_dict[port]:
                    cont += 1
                    data = str(cont) + fake_data
                    self.start_push_log_data(data, NANOMSG_PUSH_INTERFACE)
            if today != datetime.today().date():
                self.middle_night_assert_file(today)
                today = datetime.today().date()
            time.sleep(120)

    def while_true_normal_data_test_sleep_2_min(self):
        print('---circular_test_normal_logger_data---')
        fh = open(CIRCULAR_LOGGER_SERVER_SYSTEM_DATA, "w", newline='')
        writer = csv.writer(fh)
        header = ['task_end_time', '系统单核CPU使用率', 'logger_server进程CPU使用率', 'available memory',
                  'Memory Used by logger_server']
        writer.writerow(header)
        fh.close()
        del writer
        today = datetime.today().date()
        num = 0
        while True:
            normal_data_fake_dict = DataCenter.FlyData.random_port_and_content()
            num += 1
            logger.info('第{0}次运行'.format(num))
            cont = 0
            for port in normal_data_fake_dict:
                for fake_data in normal_data_fake_dict[port]:
                    cont += 1
                    data = str(cont) + fake_data
                    self.start_push_log_data(data, NANOMSG_PUSH_INTERFACE)
            usage_data = get_cpu_and_memory_usage('logger_server.exe')
            logger.info('usage_data: {0}'.format(usage_data))
            self.write_mem_usage_data_to_csv_file(CIRCULAR_LOGGER_SERVER_SYSTEM_DATA, usage_data)
            if today != datetime.today().date():
                self.middle_night_assert_file(today)
                today = datetime.today().date()
            time.sleep(120)

    # 随机端口数据压测
    def random_port_logger_data_test(self):
        count = 0
        while True:
            count += 1
            fake_data = DataCenter.FlyData.faker_data()
            fake_port = random.randint(1, 2147483645)
            data = str(fake_port) + fake_data
            self.start_push_log_data(data, NANOMSG_PUSH_INTERFACE)
            if count > 100:
                count = 0
                usage_data = get_cpu_and_memory_usage('logger_server.exe')
                logger.info('usage_data: {0}'.format(usage_data))
                self.write_mem_usage_data_to_csv_file(CIRCULAR_LOGGER_SERVER_SYSTEM_DATA, usage_data)

    def assert_file_32k_and_over_32k_data(self, file_name, source_data):
        with allure.step('日志文件名为：{0}'.format(file_name)):
            print('日志文件名为：{0}'.format(file_name))
        origin_path = os.path.join(TestLoggerService.log_path, file_name)
        if os.path.exists(origin_path):
            fh_origin = open(origin_path, 'r', encoding='utf-8', errors='ignore')
            offset = 1024 * 34
            fh_origin.seek(0, os.SEEK_END)
            file_size = fh_origin.tell()
            buf_size = min(file_size, offset)
            fh_origin.seek(file_size - buf_size)
            origin_data = fh_origin.read()
            fh_origin.close()
            # with assume:
            try:
                assert -1 != origin_data.find(source_data)
                # assert origin_data == source_data
            except AssertionError:
                with allure.step('断言错误，发送的数据：{0}，未在文件：{1}中找到'.format(source_data, file_name)):
                    print('断言错误，发送的数据：{0}，未在文件：{1}中找到'.format(source_data, file_name))
                    assert 1 == 0
            else:
                with allure.step('发送的所有数据，都可以在日志文件中找到，success'):
                    pass
                print("32k data push success")
            # os.remove(origin_path)
        else:
            with assume:
                with allure.step('未找到日志文件：{0}'.format(origin_path)):
                    print('未找到日志文件：{0}'.format(origin_path))
                    assert 1 == 0

    # @pytest.mark.skip
    @allure.step("日志服务，端口边界值测试")
    def test_boundary_logger_data(self, nng_push_host_port):
        with allure.step('nng_push_host: {0}'.format(nng_push_host_port)):
            print('nng_push_host: ', nng_push_host_port)
        TestLoggerService.nng_push_host_port = nng_push_host_port
        print('---test_boundary_logger_data---')
        with allure.step('生成测试数据'):
            boundary_data_fake_dict = DataCenter.FlyData.random_big_port_and_content()
        with allure.step('push data'):
            for port in boundary_data_fake_dict:
                for fake_data in boundary_data_fake_dict[port]:
                    data = str(port) + fake_data
                    self.start_push_log_data(data, TestLoggerService.nng_push_host_port)
        time.sleep(8)
        self.assert_port_and_log_file(boundary_data_fake_dict)

    # @pytest.mark.skip
    @allure.step("日志服务，端口正常值测试")
    def test_normal_logger_data(self, normal_data_fake_dict=None):
        print('---test_normal_logger_data---')
        if normal_data_fake_dict is None:
            with allure.step('生成测试数据'):
                normal_data_fake_dict = DataCenter.FlyData.random_port_and_content()
        with allure.step('push data'):
            for port in normal_data_fake_dict:
                for fake_data in normal_data_fake_dict[port]:
                    data = str(port) + fake_data
                    self.start_push_log_data(data, TestLoggerService.nng_push_host_port)
        time.sleep(4)
        self.assert_port_and_log_file(normal_data_fake_dict)

    # @pytest.mark.skip
    @allure.step("日志服务，32k数据测试")
    def test_logger_data_32k(self):
        print('---test_logger_data---')
        push_sock = nng.Push0(dial=TestLoggerService.nng_push_host_port)
        file = open(LOGGER_SERVER_32K_TEST_DATA, 'r')
        source_data = file.read()
        print('data_len: ', len(source_data.encode()))
        suffix_data = file.readline()
        file.close()
        push_sock.send((str(2147483644) + ' ' + source_data).encode())
        push_sock.send((str(2147483645) + ' ' + source_data + suffix_data).encode())
        time.sleep(2)
        today = datetime.today().date()
        file_name_32k_data = str(today).split('-')[1] + '-' + str(today).split('-')[2] + '-' + 'p' + str(
            2147483644) + '.log'
        file_name_over_32k_data = str(today).split('-')[1] + '-' + str(today).split('-')[2] + '-' + 'p' + str(
            2147483645) + '.log'
        with allure.step('32k边界值数据测试'):
            self.assert_file_32k_and_over_32k_data(file_name_32k_data, source_data)
        with allure.step('大于32k数据测试'):
            self.assert_file_32k_and_over_32k_data(file_name_over_32k_data, source_data)

    # 多线程压测
    # @pytest.mark.skip
    @allure.step("日志服务，多线程压测")
    def test_thread_normal_logger_data(self):
        thread_list = []
        with allure.step('生成测试数据'):
            normal_data_fake_dict = DataCenter.FlyData.random_port_and_content()
        for i in range(25):
            t = threading.Thread(target=self.test_normal_logger_data, args=(normal_data_fake_dict,))
            t.start()
            # print(threading.enumerate())
            thread_list.append(t)
        for i in thread_list:
            i.join()
        print('pressure test multithreading')

    # 多线程
    # @pytest.mark.skip
    @allure.step("日志服务，push 32K数据多线程测试")
    def test_thread_logger_data_32k(self):
        thread_list = []
        for i in range(30):
            t = threading.Thread(target=self.test_logger_data_32k)
            t.start()
            thread_list.append(t)
        for i in thread_list:
            i.join()
        print('data_32k test multithreading')

    def random_pressure_test(self):
        # TestLoggerService.nng_push_host_port = NANOMSG_PUSH_INTERFACE
        fh = open(CIRCULAR_LOGGER_SERVER_SYSTEM_DATA, "w", newline='')
        writer = csv.writer(fh)
        header = ['task_end_time', '系统单核CPU使用率', 'logger_server进程CPU使用率', 'available memory',
                  'Memory Used by logger_server']
        writer.writerow(header)
        fh.close()
        self.test_boundary_logger_data()
        while True:
            random_integer = random.randint(1, 9)
            if 3 >= random_integer:
                self.test_normal_logger_data()
            elif 6 >= random_integer:
                self.test_logger_data_32k()
            else:
                self.test_boundary_logger_data()
            usage_data = get_cpu_and_memory_usage('logger_server.exe')
            logger.info('usage_data: {0}'.format(usage_data))
            self.write_mem_usage_data_to_csv_file(CIRCULAR_LOGGER_SERVER_SYSTEM_DATA, usage_data)


if __name__ == "__main__":
    # import subprocess
    # subprocess.call(['pytest', '-s', 'test_LoggerService.py::TestLoggerService', '--alluredir', '../allurereport', '--clean-alluredir'])
    # # pytest.main(['-s', 'test_LoggerService.py::TestLoggerService', '--alluredir', '../allurereport', '--clean-alluredir'])
    # os.system('allure serve ../allurereport/')
    new_test = TestLoggerService()
    print("---start create_data---")
    DataCenter.FlyData.generate_size_32k_file()
    TestLoggerService.log_path = os.path.join(get_path_by_process_name('logger_server.exe'), 'log')
    print('log_path: ', TestLoggerService.log_path)
    new_test.random_pressure_test()
    # new_test.multithreading_circular_test()
    # new_test.circular_test_normal_logger_data()
    # new_test.random_port_logger_data_test()
    # new_test.setup_class()
    # while True:
    #     new_test.setup_class()
    #     new_test.test_normal_logger_data()
    #     new_test.test_boundary_logger_data()
    #     new_test.test_logger_data_32k()

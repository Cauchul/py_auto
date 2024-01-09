import inspect
import os

# nanomsg push接口
NANOMSG_PUSH_INTERFACE = 'tcp://127.0.0.1:8860'

# 项目根目录
PROJECT_TESTCASE_DIR = os.path.abspath(os.path.curdir)
PROJECT_BASE = os.path.abspath(os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), ".."))

# 循环测试，内存和cpu信息保存文件
LOGGER_SERVER_32K_TEST_DATA = os.path.join(PROJECT_TESTCASE_DIR, r'logger_server_test_data\logger_test_32k_data.txt')
CIRCULAR_LOGGER_SERVER_SYSTEM_DATA = os.path.join(PROJECT_TESTCASE_DIR, r'logger_server_test_data\logger_server_CPU_and_memory_usage_data.csv')
MULTITHREADING_CIRCULAR_LOGGER_SERVER_SYSTEM_DATA = os.path.join(PROJECT_TESTCASE_DIR, r'logger_server_test_data\multithreading_logger_server_CPU_and_memory_usage_data.csv')

# 日志目录
CIRCULAR_LOG_NAME = os.path.join(PROJECT_TESTCASE_DIR, r'logger_server_test_data\logger_server_circular_test.log')


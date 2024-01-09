import random

from faker import Faker

from TestCase.GobalVariabies import *


class DataCenter:
    # class StaticData:
    #
    # class DataPool:
    class FlyData:
        @staticmethod
        def faker_data():
            fake = Faker('zh_CN')
            name = fake.name()
            passwd = fake.password(special_chars=True)
            sid = fake.ssn()
            email = fake.email()
            sentence = fake.sentence()
            card_id_fake = fake.country_code()
            service_fake = fake.bs()
            process_fake = fake.company_prefix() + "(" + str(fake.random_int()) + ")"
            date_fake = fake.date_time().strftime("%Y-%m-%d, %H:%M:%S")
            file_fake = fake.country() + ":" + str(fake.random_int())
            log_content = fake.pystr()
            return ' ' + name + passwd + sid + card_id_fake + service_fake + email + sentence + process_fake + date_fake + file_fake + log_content + '\n'

        @staticmethod
        def random_port_and_content(size=50):
            data_fake_dict = {}
            for i in range(size):
                port_fake = random.randint(1, 2147483645)
                data_fake_dict[port_fake] = []
                for num in range(2):
                    normal_data = DataCenter.FlyData.faker_data()
                    data_fake_dict[port_fake].append(normal_data)
            return data_fake_dict

        @staticmethod
        def random_big_port_and_content(size=5):
            data_fake_dict = {2147483646: [DataCenter.FlyData.faker_data()], 2147483647: [DataCenter.FlyData.faker_data()], 2147483648: [DataCenter.FlyData.faker_data()]}
            for i in range(size):
                port_fake = random.randint(2147483649, 9999999999)
                data_fake_dict[port_fake] = []
                normal_data = DataCenter.FlyData.faker_data()
                data_fake_dict[port_fake].append(normal_data)
            return data_fake_dict

        @staticmethod
        def generate_size_32k_file():
            if not os.path.exists(os.path.join(PROJECT_BASE, 'TestData')):
                os.makedirs(os.path.join(PROJECT_BASE, 'TestData'))
            if os.path.exists(LOGGER_SERVER_32K_TEST_DATA):
                os.remove(LOGGER_SERVER_32K_TEST_DATA)
            offset = 1029 * 32 - 1
            fh = open(LOGGER_SERVER_32K_TEST_DATA, 'w+', encoding='utf-8', errors='ignore')
            file_size = 0
            while file_size < 33*1024:
                fh.write(DataCenter.FlyData.faker_data())  # 文件写了之后，文件指针就会往后移动
                file_size = fh.tell()
            fh.seek(file_size - offset)  # 减少是把文件指针往回移动
            data = fh.read()  # 从当前位置往后读
            fh.close()
            ff = open(LOGGER_SERVER_32K_TEST_DATA, 'w')
            ff.write(data)
            ff.close()

        @staticmethod
        def generate_redis_data():  # 生成key/value redis数据
            fake = Faker('zh_CN')
            key = random.randint(0, 99999)
            data = fake.pystr()
            return str(key), data

        def generate_json_data(self):  # 生成json格式的数据
            pass

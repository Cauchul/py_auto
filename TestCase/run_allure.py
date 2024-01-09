import pytest
import os

if __name__ == "__main__":
    pytest.main(['-vs', 'test_DCSSystemMgr.py', '--alluredir', '../allurereport', '--clean-alluredir'])
    os.system('allure serve ../allurereport/')

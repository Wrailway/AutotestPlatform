import pytest
import time
import math
import os
from datetime import datetime
from server.server_common import OperateSharedData

# 全局参数
execute_times = 1
operate_interval = 1
threads_num = 1

def refresh_params():
    global execute_times, operate_interval, threads_num
    execute_times, operate_interval,threads_num = OperateSharedData.read_fun_params()

def random_sleep():
    refresh_params()
    time.sleep(operate_interval)

# ========================= 工具函数 =========================
def complex_calculate(n):
    random_sleep()
    factorial = math.factorial(n)
    square_sum = sum(i**2 for i in range(1, n+1))
    log_val = math.log(n+1) if n>0 else 0
    return factorial + square_sum + log_val

def string_process(s):
    random_sleep()
    return s.strip().upper().replace(" ", "_")

def list_operation(lst):
    random_sleep()
    unique = sorted(list(set(lst)))
    return sum(unique) * len(unique)

def dict_validate(d):
    random_sleep()
    return "name" in d and "age" in d and isinstance(d["age"], int)

def file_simulate_write(content):
    random_sleep()
    return len(content) > 0

# ========================= 检查暂停/停止 =========================
def check_stop_pause():
    stop, pause = OperateSharedData.read_control()
    if stop:
        pytest.exit("测试已停止")
    while pause:
        time.sleep(0.2)
        stop, pause = OperateSharedData.read_control()
        if stop:
            pytest.exit("测试已停止")

@pytest.fixture(autouse=True)
def auto_check():
    check_stop_pause()

# ========================= 核心：每次都执行 assert =========================
def run_repeat(func):
    refresh_params()
    for _ in range(execute_times):
        check_stop_pause()
        result = func()
        assert result, "用例执行失败"  # ✅ 这里统一断言，绝对不报错

# ========================= 25 条成功用例 =========================
def test_success_01():
    run_repeat(lambda: complex_calculate(3) == pytest.approx(6 + 14 + 1.386))

def test_success_02():
    run_repeat(lambda: complex_calculate(5) > 150)

def test_success_03():
    run_repeat(lambda: string_process("  hello test  ") == "HELLO_TEST")

def test_success_04():
    run_repeat(lambda: string_process("PYTEST") == "PYTEST")

def test_success_05():
    run_repeat(lambda: list_operation([1,2,2,3,3,3]) == 18)

def test_success_06():
    run_repeat(lambda: list_operation([10,20,30]) == 180)

def test_success_07():
    run_repeat(lambda: dict_validate({"name":"a","age":20}) is True)

def test_success_08():
    run_repeat(lambda: dict_validate({"name":"x","age":0}) is True)

def test_success_09():
    run_repeat(lambda: file_simulate_write("test content") is True)

def test_success_10():
    run_repeat(lambda: file_simulate_write(" ") is True)

def test_success_11():
    run_repeat(lambda: datetime.now().year >= 2020)

def test_success_12():
    run_repeat(lambda: abs(-123.45) == 123.45)

def test_success_13():
    run_repeat(lambda: round(3.14159, 2) == 3.14)

def test_success_14():
    run_repeat(lambda: max([9,5,11,2]) == 11)

def test_success_15():
    run_repeat(lambda: min([9,5,11,2]) == 2)

def test_success_16():
    run_repeat(lambda: "test".isalpha() is True)

def test_success_17():
    run_repeat(lambda: "123".isdigit() is True)

def test_success_18():
    run_repeat(lambda: [1,2,3] + [4,5] == [1,2,3,4,5])

def test_success_19():
    run_repeat(lambda: {"a":1} | {"b":2} == {"a":1,"b":2})

def test_success_20():
    run_repeat(lambda: os.path.exists(".") is True)

def test_success_21():
    run_repeat(lambda: len(str(datetime.now())) > 10)

def test_success_22():
    run_repeat(lambda: math.sqrt(16) == 4.0)

def test_success_23():
    run_repeat(lambda: math.pow(2, 10) == 1024.0)

def test_success_24():
    run_repeat(lambda: isinstance([1,2,3], list) is True)

def test_success_25():
    run_repeat(lambda: isinstance(123, int) is True)

# ========================= 25 条失败用例 =========================
def test_fail_26():
    run_repeat(lambda: complex_calculate(3) == 9999)

def test_fail_27():
    run_repeat(lambda: complex_calculate(5) < 10)

def test_fail_28():
    run_repeat(lambda: string_process(" hi ") == "hi")

def test_fail_29():
    run_repeat(lambda: string_process("test") == "Test")

def test_fail_30():
    run_repeat(lambda: list_operation([1,1,1]) == 10)

def test_fail_31():
    run_repeat(lambda: list_operation([2,4,6]) == 0)

def test_fail_32():
    run_repeat(lambda: dict_validate({"name":"a"}) is True)

def test_fail_33():
    run_repeat(lambda: dict_validate({"age":20}) is True)

def test_fail_34():
    run_repeat(lambda: file_simulate_write("") is True)

def test_fail_35():
    run_repeat(lambda: file_simulate_write(None) is True)

def test_fail_36():
    run_repeat(lambda: datetime.now().year == 2000)

def test_fail_37():
    run_repeat(lambda: abs(-123) == -123)

def test_fail_38():
    run_repeat(lambda: round(2.718, 1) == 2.71)

def test_fail_39():
    run_repeat(lambda: max([1,2,3]) == 2)

def test_fail_40():
    run_repeat(lambda: min([1,2,3]) == 2)

def test_fail_41():
    run_repeat(lambda: "test123".isalpha() is True)

def test_fail_42():
    run_repeat(lambda: "123abc".isdigit() is True)

def test_fail_43():
    run_repeat(lambda: [1] + [2] == [1,2,3])

def test_fail_44():
    run_repeat(lambda: {"x":1} | {"y":2} == {"x":1})

def test_fail_45():
    run_repeat(lambda: os.path.exists("not_exist.txt") is True)

def test_fail_46():
    run_repeat(lambda: len(str(datetime.now())) < 5)

def test_fail_47():
    run_repeat(lambda: math.sqrt(9) == 2)

def test_fail_48():
    run_repeat(lambda: math.pow(3,3) == 9)

def test_fail_49():
    run_repeat(lambda: isinstance(123, str) is True)

def test_fail_50():
    run_repeat(lambda: isinstance("abc", int) is True)
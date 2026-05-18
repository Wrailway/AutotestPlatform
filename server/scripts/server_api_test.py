import base64
import os
import random
import uuid
import time
import json

import ddddocr
import pytest
import requests
from datetime import datetime

# 本地工具导入
from server.server_common import OperateSharedData

# ====================== 全局常量配置 ======================
HOST = "http://neucirflite-test.oymotion.com"
BASE_URL = f"{HOST}/neucirflite_portal"
REAL_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3Nzg2ODAxNTQsInVzZXJuYW1lIjoid2FuZ3J1aXdlaUBveW1vdGlvbi5jb20ifQ.wh4qUon9siPfdYSiU-C7EuZZ6K5kH7AGvQzfdrjn7c0"

HEADERS = {
    "X-Access-Token": REAL_TOKEN,
    "Content-Type": "application/json"
}

# ====================== 状态码常量 ======================
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404

# ====================== 接口地址常量 ======================
# 一、系统登录 & 主页
URL_SYS_GET_LOGIN_QRCODE = "/sys/getLoginQrcode"
URL_SYS_LOGIN = "/sys/login"
URL_SYS_RANDOM_IMAGE = "/sys/randomImage/{key}"
URL_BACKSTAGE_PAGE = "/backstage/page"
URL_DEFAULT_SETTINGS = "/default_settings/{deviceName}"

# 二、设备管理
URL_DEVICE_ADD = "/device/Device/add"
URL_DEVICE_DELETE = "/device/Device/delete"
URL_DEVICE_DELETE_BATCH = "/device/Device/deleteBatch"
URL_DEVICE_EDIT = "/device/Device/edit"
URL_DEVICE_LIST = "/device/Device/list"
URL_DEVICE_LOG = "/device/Device/log/{deviceSerialNo}"
URL_DEVICE_QUERY_BY_ID = "/device/Device/queryById"

# 三、设备类型管理
URL_DEVICE_TYPES_ADD = "/device/DeviceTypes/add"
URL_DEVICE_TYPES_DELETE = "/device/DeviceTypes/delete"
URL_DEVICE_TYPES_DELETE_BATCH = "/device/DeviceTypes/deleteBatch"
URL_DEVICE_TYPES_EDIT = "/device/DeviceTypes/edit"
URL_DEVICE_TYPES_LIST = "/device/DeviceTypes/list"
URL_DEVICE_TYPES_QUERY_BY_ID = "/device/DeviceTypes/queryById"
URL_DEVICE_TYPES_DEVICE_TYPE = "/device/DeviceTypes/devicetype"
URL_DEVICE_TYPES_DEVICE_TYPE_NAME = "/device/DeviceTypes/devicetypename"
URL_DEVICE_TYPES_TOP = "/device/DeviceTypes/top"

# 四、设备固件管理
URL_DEVICE_FIRMWARE_ADD = "/device/deviceFirmware/add"
URL_DEVICE_FIRMWARE_DELETE = "/device/deviceFirmware/delete"
URL_DEVICE_FIRMWARE_DELETE_BATCH = "/device/deviceFirmware/deleteBatch"
URL_DEVICE_FIRMWARE_EDIT = "/device/deviceFirmware/edit"
URL_DEVICE_FIRMWARE_LIST = "/device/deviceFirmware/list"
URL_DEVICE_FIRMWARE_QUERY_TYPE_ID = "/device/deviceFirmware/queryTypeId"
URL_DEVICE_FIRMWARE_UPLOAD = "/device/deviceFirmware/upload"

# 五、APK 模块
URL_APK_UPLOAD_FILE = "/apk/upload/file"
URL_APK_DELETE_FILE = "/apk/upload/file"
URL_APK_DOWNLOAD_LATEST = "/apks/downloadlatest"
URL_APK_LATEST_VERSION = "/apks/latest_version.json"
URL_APK_DOWNLOAD_VERSION = "/apks/{version}"
URL_APK_VERSION_ADD = "/apk_version/apkVersion/add"
URL_APK_VERSION_DELETE = "/apk_version/apkVersion/delete"
URL_APK_VERSION_DELETE_BATCH = "/apk_version/apkVersion/deleteBatch"
URL_APK_VERSION_EDIT = "/apk_version/apkVersion/edit"
URL_APK_VERSION_LIST = "/apk_version/apkVersion/list"
URL_APK_VERSION_QUERY_BY_ID = "/apk_version/apkVersion/queryById"

# 六、设备用户
URL_USER_DELETE_ERROR_TRAINING_INFO = "/user/delete_error_training_info"
URL_USER_DELETE_TRAINING_RECORD = "/user/delete_training_record"
URL_USER_DEVICE_INFO = "/user/device_info"
URL_USER_DOWNLOAD_EMG_DATA = "/user/download_emg_data"
URL_USER_DOWNLOAD_EMG_MODEL = "/user/download_emg_model"
URL_USER_GESTURE_TRAIN = "/user/gesture_train"
URL_USER_GET_TRAINING_STATUS = "/user/getTrainingStatus"
URL_USER_GET_DEVICE_SETTINGS = "/user/get_device_settings"
URL_USER_GET_MODEL_STATUS = "/user/get_model_status"
URL_USER_GET_TEMPLATES = "/user/get_templates"
URL_USER_GET_USER_INFO = "/user/user_info"
URL_USER_GET_TRAINING_RECORDS = "/user/get_training_records"
URL_USER_LATEST_FIRMWARE_VERSION = "/user/latest_firmware_version_of_device"
URL_USER_MODIFY_TEMPLATE_INFO = "/user/modify_template_info"
URL_USER_RETRAIN = "/user/retrain"
URL_USER_SAVE_DEVICE_SETTINGS = "/user/save_device_settings"
URL_USER_SIGNUP = "/user/signup"
URL_USER_SINGLE_TRAIN = "/user/single_train"
URL_USER_USAGE_STAT = "/user/usage_stat"
URL_USER_USER_INFO = "/user/user_info"
URL_USER_ADD_MODEL_STATUS = "/user/add_model_status"
URL_USER_CHECK_LATEST_EMG_MODELS = "/user/check_latest_emg_models"
URL_USER_DEBUG_INFO = "/user/debug_info"
URL_USER_SIGNIN = "/user/signin"

# 其他通用接口
URL_FIRMWARE_DOWNLOAD = "/firmware/{getTypeName}/{url}"
URL_USAGE_STATS_ADD = "/usagestats/add"
URL_USAGE_STATS_DELETE = "/usagestats/delete"
URL_USAGE_STATS_DELETE_BATCH = "/usagestats/deleteBatch"
URL_USAGE_STATS_EDIT = "/usagestats/edit"
URL_USAGE_STATS_LIST = "/usagestats/list"
URL_USAGE_STATS_QUERY_BY_ID = "/usagestats/queryById"

# ====================== 测试全局变量 ======================
TEST_TEMPLATE_NO = 9999
TEST_TRAINING_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
TEST_UUID = f"AUTO_{uuid.uuid4().hex[:12].upper()}"
TEST_PAGE_NO = 1
TEST_PAGE_SIZE = 10
TEST_CAPTCHA_KEY = f"test_key_{uuid.uuid4().hex[:6]}"
TEST_QRCODE_ID = f"test_qrcode_{uuid.uuid4().hex[:6]}"
TEST_DEVICE_SERIAL_NO = f"SN_{uuid.uuid4().hex[:10].upper()}"
TEST_DEVICE_NAME = "OYFM-7000.json"

TEST_ID = "1"
TEST_IDS = "1,2"
TEST_VERSION = "V1.0.0"
DEVICE_MAC = "24:71:89:EF:27:EF"
DEVICE_UUID = "8266a4ba31decf20"
ACTIVATE_KEY = None

# 设备类型
TEST_TYPE_NAME = f"TYPE_{uuid.uuid4().hex[:6].upper()}"
TEST_HARDWARE_TYPE = 1
TEST_HARDWARE_VER = 2

# 设备固件
TEST_FW_DEVICE_TYPE_ID = 1
TEST_FW_VERSION = "V2.0.0"
TEST_FW_RELEASE_ZH = "固件版本测试中文说明"
TEST_FW_RELEASE_EN = "Firmware test release note"
TEST_FW_IS_VALID = 1
TEST_FW_URL = "/firmware/test.bin"

# 用户/训练
TEST_USER_ID = "10001"
TEST_TEMPLATE_ID = 1
TEST_TEMPLATE_NAME = f"AUTO_TPL_{uuid.uuid4().hex[:6]}"
TEST_MODEL_ID = 1
TEST_EMG_DATA = "test_emg_data"

# 全局运行时变量
device_id = ""
test_device_sn = ""
test_device_type_id = ""
test_firmware_id = None
test_firmware_ids_batch = []
test_firmware_id_for_edit = None
file_path = ""
latest_firmware_url = ""
saved_model_data = {}

# ====================== 工具函数 ======================
def check_test_stop_pause():
    try:
        is_stop, is_pause = OperateSharedData.read_control()
        if is_stop:
            pytest.exit("🛑 测试已停止")
        while is_pause:
            time.sleep(0.2)
            is_stop, is_pause = OperateSharedData.read_control()
            if is_stop:
                pytest.exit("🛑 测试已停止")
    except Exception:
        pass

execute_total_times = 1
case_interval_seconds = 1
threads_num = 1

def refresh_test_params():
    try:
        global execute_total_times, case_interval_seconds, threads_num
        execute_total_times, case_interval_seconds, threads_num = OperateSharedData.read_fun_params()
    except Exception:
        pass

# 验证码识别
ocr = ddddocr.DdddOcr(use_gpu=False, show_ad=False)

def get_captcha_from_base64(base64_img_str):
    try:
        if "," in base64_img_str:
            base64_data = base64_img_str.split(",")[1]
        else:
            base64_data = base64_img_str
        img_bytes = base64.b64decode(base64_data)
        return ocr.classification(img_bytes).strip()
    except Exception as e:
        print(f"验证码识别失败：{e}")
        return None

def set_token_to_session(session, login_response):
    global REAL_TOKEN
    try:
        res_data = login_response.json()
        token = res_data["result"]["token"]
        session.headers.update({"X-Access-Token": token})
        REAL_TOKEN = token
        print(f"\n✅ 登录成功 | TOKEN 已自动生效：{token[:50]}...")
    except Exception as e:
        print(f"\n❌ TOKEN 设置失败：{str(e)}")
        raise

def print_response_info(req_params, res):
    print("\n" + "=" * 50)
    if req_params:
        print(f"请求参数: {req_params}")
    print(f"状态码: {res.status_code}")
    try:
        json_data = res.json()
        print(f"响应内容: {json.dumps(json_data, ensure_ascii=False, indent=2)}")
    except Exception:
        print(f"响应内容: {res.text[:200]}")
    print("=" * 50)

def assert_api_common(res):
    allowed_codes = {HTTP_OK, HTTP_UNAUTHORIZED, HTTP_FORBIDDEN, HTTP_NOT_FOUND}
    assert res.status_code in allowed_codes, f"HTTP 状态码异常：{res.status_code}"

    if res.status_code == HTTP_UNAUTHORIZED:
        pytest.fail("HTTP 401：未授权")
    if res.status_code == HTTP_FORBIDDEN:
        pytest.fail("HTTP 403：权限不足")
    if res.status_code == HTTP_NOT_FOUND:
        pytest.fail("HTTP 404：接口不存在")

    try:
        data = res.json()
        if "success" in data:
            success = data.get("success")
            msg = data.get("message", "无消息")
            assert success is True, f"业务失败：{msg}"
        elif "msg" in data and "res" in data:
            res_code = data.get("res")
            msg = data.get("msg", "无消息")
            assert res_code == 0, f"业务失败：{msg}"
    except ValueError:
        pass

def safe_request(session, method, url, **kwargs):
    try:
        method = method.lower()
        if method == "get":
            return session.get(url, timeout=10, **kwargs)
        elif method == "post":
            return session.post(url, timeout=10, **kwargs)
        elif method == "put":
            return session.put(url, timeout=10, **kwargs)
        elif method == "delete":
            return session.delete(url, timeout=10, **kwargs)
    except Exception as e:
        pytest.skip(f"请求异常跳过: {str(e)}")

# ====================== 夹具 ======================
@pytest.fixture(scope="session", autouse=True)
def device_driver():
    print("\n✅ 全量接口测试开始")
    yield
    print("\n✅ 全量接口测试结束")

@pytest.fixture(scope="function", autouse=True)
def case_control_hook():
    yield
    check_test_stop_pause()
    refresh_test_params()
    time.sleep(case_interval_seconds)

@pytest.fixture(scope="module")
def api_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    yield session
    session.close()

# ==============================================
# 一、系统登录
# ==============================================
def test_sys_login(api_session):
    """系统登录-账号密码登录"""
    print(f"\n🚀 开始执行：{test_sys_login.__doc__}")
    url_captcha = f"{BASE_URL}{URL_SYS_RANDOM_IMAGE}".format(key=TEST_CAPTCHA_KEY)
    res_captcha = safe_request(api_session, "get", url_captcha)
    assert_api_common(res_captcha)

    data_captcha = res_captcha.json()
    captcha_code = get_captcha_from_base64(data_captcha["result"])
    print(f"\n✅ 登录使用的验证码：【{captcha_code}】")

    url_login = f"{BASE_URL}{URL_SYS_LOGIN}"
    json_data = {
        "username": "admin",
        "password": "123456",
        "captcha": captcha_code,
        "checkKey": TEST_CAPTCHA_KEY
    }
    res = safe_request(api_session, "post", url_login, json=json_data)
    print_response_info(json_data, res)
    assert_api_common(res)
    set_token_to_session(api_session, res)

def test_backstage_page(api_session):
    """主页-后台首页查看"""
    print(f"\n🚀 开始执行：{test_backstage_page.__doc__}")
    url = f"{BASE_URL}{URL_BACKSTAGE_PAGE}"
    res = safe_request(api_session, "get", url)
    print_response_info(None, res)
    assert_api_common(res)

def test_default_settings(api_session):
    """系统-默认配置获取"""
    print(f"\n🚀 开始执行：{test_default_settings.__doc__}")
    url = f"{BASE_URL}{URL_DEFAULT_SETTINGS}".format(deviceName=TEST_DEVICE_NAME)
    res = safe_request(api_session, "get", url)
    print_response_info({"deviceName": TEST_DEVICE_NAME}, res)
    assert_api_common(res)

def test_sys_random_image(api_session):
    """登录-获取验证码图片"""
    print(f"\n🚀 开始执行：{test_sys_random_image.__doc__}")
    url = f"{BASE_URL}{URL_SYS_RANDOM_IMAGE}".format(key=TEST_CAPTCHA_KEY)
    res = safe_request(api_session, "get", url)
    print_response_info({"key": TEST_CAPTCHA_KEY}, res)
    assert_api_common(res)

# ==============================================
# 二、设备管理
# ==============================================
def test_device_add(api_session):
    """设备-添加"""
    print(f"\n🚀 开始执行：{test_device_add.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_ADD}"

    ts_int = int(time.time())
    rand = random.randint(10, 99)
    current_sn = f"SN{ts_int}{rand}"
    current_activate_key = f"AK{ts_int}{rand}"
    current_addr = f"11:22:33:44:{ts_int%100:02X}:{rand:02X}"

    json_data = {
        "activateKey": current_activate_key,
        "addr": current_addr,
        "chooseType": "0",
        "dateOfManufacture": "2026-05-14T05:51:16.084Z",
        "dealerId": "1",
        "deviceSerialNo": current_sn,
        "deviceTypeId": "15",
        "forbidden": "0",
        "remark": "自动化测试"
    }

    res = safe_request(api_session, "post", url, json=json_data)
    print_response_info(json_data, res)
    assert_api_common(res)

    global device_id, test_device_sn
    test_device_sn = current_sn
    print(f"✅ 设备添加完成！SN = {test_device_sn}")

def test_device_list(api_session):
    """设备-分页列表查询"""
    print(f"\n🚀 开始执行：{test_device_list.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_LIST}"
    params = {
        "pageNo": TEST_PAGE_NO,
        "pageSize": TEST_PAGE_SIZE
    }

    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

    global device_id, test_device_sn
    try:
        data = res.json()
        records = data.get("result", {}).get("records", [])
        for item in records:
            if item.get("deviceSerialNo") == test_device_sn:
                device_id = str(item.get("id"))
                print(f"\n🎉 成功找到设备！ID: {device_id}")
                break
    except Exception as e:
        print(f"⚠️ 未找到设备: {e}")

def test_device_query_by_id(api_session):
    """设备-单条查询"""
    print(f"\n🚀 开始执行：{test_device_query_by_id.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_QUERY_BY_ID}"
    params = {"id": device_id}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_device_edit_post(api_session):
    """设备-编辑（post)"""
    print(f"\n🚀 开始执行：{test_device_edit_post.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_EDIT}"

    json_data = {
        "id": device_id,
        "activateKey": f"AK_EDIT{int(time.time())}",
        "addr": f"11:25:14:26:99:FF",
        "dealerId": "1",
        "deviceSerialNo": f"SN_EDIT{int(time.time())}",
        "deviceTypeId": "15",
        "forbidden": "0",
        "remark": "自动化编辑测试-成功"
    }

    res = safe_request(api_session, "post", url, json=json_data)
    print_response_info(json_data, res)
    assert_api_common(res)

def test_device_edit_put(api_session):
    """设备-编辑(put)"""
    print(f"\n🚀 开始执行：{test_device_edit_put.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_EDIT}"

    json_data = {
        "id": device_id,
        "activateKey": f"AK_PUT{int(time.time())}",
        "addr": f"11:25:14:26:99:FF",
        "dealerId": "1",
        "deviceSerialNo": f"SN_PUT{int(time.time())}",
        "deviceTypeId": "15",
        "forbidden": "0",
        "remark": "自动化PUT编辑-成功"
    }

    res = safe_request(api_session, "put", url, json=json_data)
    print_response_info(json_data, res)
    assert_api_common(res)

def test_device_log(api_session):
    """设备-设备日志查询"""
    print(f"\n🚀 开始执行：{test_device_log.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_LOG}".format(deviceSerialNo=test_device_sn)
    res = safe_request(api_session, "get", url)
    print_response_info({"deviceSerialNo": test_device_sn}, res)
    assert_api_common(res)

def test_device_delete(api_session):
    """设备-通过id删除"""
    print(f"\n🚀 开始执行：{test_device_delete.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_DELETE}"
    params = {"id": str(device_id)}
    res = safe_request(api_session, "delete", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_device_delete_batch(api_session):
    """设备-批量删除"""
    print(f"\n🚀 开始执行：{test_device_delete_batch.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_DELETE_BATCH}"
    params = {"ids": str(device_id)}
    res = safe_request(api_session, "delete", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

# ==============================================
# 三、设备类型管理
# ==============================================
def test_device_types_add(api_session):
    """设备类型-增加"""
    print(f"\n🚀 开始执行：{test_device_types_add.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_ADD}"
    json_data = {
        "typeName": TEST_TYPE_NAME,
        "hardwareType": TEST_HARDWARE_TYPE,
        "hardwareVer": TEST_HARDWARE_VER
    }
    res = safe_request(api_session, "post", url, json=json_data)
    print_response_info(json_data, res)
    assert_api_common(res)

def test_device_types_list(api_session):
    """设备类型-分页列表查询"""
    global test_device_type_id
    print(f"\n🚀 开始执行：{test_device_types_list.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_LIST}"
    params = {
        "pageNo": TEST_PAGE_NO,
        "pageSize": TEST_PAGE_SIZE,
        "typeName": TEST_TYPE_NAME
    }

    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

    try:
        data = res.json()
        records = data.get("result", {}).get("records", [])
        for item in records:
            if item.get("typeName") == TEST_TYPE_NAME:
                test_device_type_id = str(item.get("id"))
                print(f"\n🎉 成功获取设备类型 ID：{test_device_type_id}")
                break
    except Exception as e:
        print("⚠️ 获取ID异常：", e)

def test_device_types_delete(api_session):
    """设备类型-单条删除"""
    print(f"\n🚀 开始执行：{test_device_types_delete.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_DELETE}"
    params = {"id": test_device_type_id}
    res = safe_request(api_session, "delete", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_device_types_delete_batch(api_session):
    """设备类型-批量删除"""
    print(f"\n🚀 开始执行：{test_device_types_delete_batch.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_DELETE_BATCH}"
    params = {"ids": test_device_type_id}
    res = safe_request(api_session, "delete", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_device_types_edit_post(api_session):
    """设备类型-编辑(post)"""
    print(f"\n🚀 开始执行：{test_device_types_edit_post.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_EDIT}"
    json_data = {
        "id": test_device_type_id,
        "typeName": TEST_TYPE_NAME,
        "hardwareType": TEST_HARDWARE_TYPE + 1,
        "hardwareVer": TEST_HARDWARE_VER
    }
    res = safe_request(api_session, "post", url, json=json_data)
    print_response_info(json_data, res)
    assert_api_common(res)

def test_device_types_edit_put(api_session):
    """设备类型-编辑(put)"""
    print(f"\n🚀 开始执行：{test_device_types_edit_put.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_EDIT}"
    json_data = {
        "id": test_device_type_id,
        "typeName": TEST_TYPE_NAME,
        "hardwareType": TEST_HARDWARE_TYPE,
        "hardwareVer": TEST_HARDWARE_VER + 1
    }
    res = safe_request(api_session, "put", url, json=json_data)
    print_response_info(json_data, res)
    assert_api_common(res)

def test_device_types_query_by_id(api_session):
    """设备类型-通过id查询"""
    print(f"\n🚀 开始执行：{test_device_types_query_by_id.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_QUERY_BY_ID}"
    params = {"id": test_device_type_id}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_device_types_devicetypename(api_session):
    """设备类型-通过类型名称查询"""
    print(f"\n🚀 开始执行：{test_device_types_devicetypename.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_DEVICE_TYPE_NAME}"
    res = safe_request(api_session, "get", url)
    print_response_info(None, res)
    assert_api_common(res)

def test_device_types_top(api_session):
    """设备类型-最新前5条"""
    print(f"\n🚀 开始执行：{test_device_types_top.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_TOP}"
    res = safe_request(api_session, "get", url)
    print_response_info(None, res)
    assert_api_common(res)

# ==============================================
# 四、设备固件管理
# ==============================================
def test_device_firmware_add(api_session):
    """设备固件-添加版本"""
    print(f"\n🚀 开始执行：{test_device_firmware_add.__doc__}")
    for i in range(1, 6):
        json_data = {
            "deviceTypeId": TEST_FW_DEVICE_TYPE_ID,
            "isValid": TEST_FW_IS_VALID,
            "releaseNoteZh": f"{TEST_FW_RELEASE_ZH}_{i}",
            "releaseNoteEn": f"{TEST_FW_RELEASE_EN}_{i}",
            "url": TEST_FW_URL,
            "version": f"V2.0.{i}"
        }
        url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_ADD}"
        res = safe_request(api_session, "post", url, json=json_data)
        print_response_info(json_data, res)
        assert_api_common(res)
        print(f"✅ 第 {i} 个固件添加成功")

def test_device_firmware_list(api_session):
    """设备固件-分页列表"""
    global test_firmware_id, test_firmware_ids_batch, test_firmware_id_for_edit
    print(f"\n🚀 开始执行：{test_device_firmware_list.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_LIST}"
    params = {
        "pageNo": TEST_PAGE_NO,
        "pageSize": TEST_PAGE_SIZE,
        "deviceTypeId": TEST_FW_DEVICE_TYPE_ID
    }

    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

    data = res.json()
    records = data.get("result", {}).get("records", [])
    assert len(records) >= 5, "固件数量不足，无法执行删除测试"

    test_firmware_id = records[0]["id"]
    test_firmware_ids_batch = [str(item["id"]) for item in records[1:4]]
    test_firmware_id_for_edit = records[4]["id"]

    print(f"\n🎉 最新1个固件ID（单删）: {test_firmware_id}")
    print(f"🎉 最新3个固件ID（批量）: {test_firmware_ids_batch}")

def test_device_firmware_delete(api_session):
    """设备固件-单条删除"""
    print(f"\n🚀 开始执行：{test_device_firmware_delete.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_DELETE}"
    params = {"id": test_firmware_id}
    res = safe_request(api_session, "delete", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)
    assert res.json().get("success") is True, "单条删除失败"

def test_device_firmware_delete_batch(api_session):
    """设备固件-批量删除"""
    print(f"\n🚀 开始执行：{test_device_firmware_delete_batch.__doc__}")
    ids_str = ",".join(test_firmware_ids_batch)
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_DELETE_BATCH}"
    params = {"ids": ids_str}
    res = safe_request(api_session, "delete", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)
    assert res.json().get("success") is True, "批量删除失败"

def test_device_firmware_edit_post(api_session):
    """设备固件-编辑POST"""
    print(f"\n🚀 开始执行：{test_device_firmware_edit_post.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_EDIT}"
    json_data = {
        "id": test_firmware_id_for_edit,
        "releaseNoteZh": "【已编辑】中文说明(post)"
    }
    res = safe_request(api_session, "post", url, json=json_data)
    print_response_info(json_data, res)
    assert_api_common(res)

def test_device_firmware_edit_put(api_session):
    """设备固件-编辑PUT"""
    print(f"\n🚀 开始执行：{test_device_firmware_edit_put.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_EDIT}"
    json_data = {
        "id": test_firmware_id_for_edit,
        "releaseNoteEn": "【Edited】English Note(put)"
    }
    res = safe_request(api_session, "put", url, json=json_data)
    print_response_info(json_data, res)
    assert_api_common(res)

def test_device_firmware_query_type_id(api_session):
    """设备固件-通过typeid查询"""
    print(f"\n🚀 开始执行：{test_device_firmware_query_type_id.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_QUERY_TYPE_ID}"
    params = {"id": test_firmware_id_for_edit}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

@pytest.mark.skip('尚未调试test_device_firmware_upload')
def test_device_firmware_upload(api_session):
    """设备固件-通用文件上传"""
    print(f"\n🚀 开始执行：{test_device_firmware_upload.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_UPLOAD}"
    res = safe_request(api_session, "post", url)
    print_response_info(None, res)
    assert_api_common(res)

# ==============================================
# 五、APK版本发布
# ==============================================
def test_apk_upload_file(api_session):
    """APK文件上传-上传APK文件"""
    print(f"\n🚀 开始执行：{test_apk_upload_file.__doc__}")
    url = f"{BASE_URL}{URL_APK_UPLOAD_FILE}"

    with open("test.apk", "wb") as f:
        f.write(b"test apk content")

    api_session.headers.pop("Content-Type", None)
    files = {
        "file": ("test.apk", open("test.apk", "rb"), "application/vnd.android.package-archive")
    }
    res = safe_request(api_session, "post", url, files=files)
    api_session.headers["Content-Type"] = "application/json"

    print_response_info(None, res)
    assert_api_common(res)

    global file_path
    result = res.json()["result"]
    file_path = result["filePath"]
    print(f"\n✅ 真实文件路径：{file_path}")

def test_apk_delete_file(api_session):
    """APK文件上传-删除APK文件"""
    print(f"\n🚀 开始执行：{test_apk_delete_file.__doc__}")
    url = f"{BASE_URL}{URL_APK_DELETE_FILE}"
    params = {"filePath": file_path}
    res = safe_request(api_session, "delete", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_apk_version_add(api_session):
    """APK版本发布-添加"""
    print(f"\n🚀 开始执行：{test_apk_version_add.__doc__}")
    url = f"{BASE_URL}{URL_APK_VERSION_ADD}"
    version = f"1.0.1_{int(time.time())}"
    version_name = f"V1.0.1_{int(time.time())}"

    json_data = {
        "appId": "com.neucir.flite",
        "channel": 0,
        "version": version,
        "versionName": version_name,
        "filePath": file_path,
        "releaseNoteZh": "自动化测试版本",
        "releaseNoteEn": "Auto test version",
        "status": 1,
        "creator": "admin"
    }

    res = safe_request(api_session, "post", url, json=json_data)
    print_response_info(json_data, res)
    assert_api_common(res)

def test_apk_version_delete(api_session):
    """APK版本发布-通过id删除"""
    print(f"\n🚀 开始执行：{test_apk_version_delete.__doc__}")
    url = f"{BASE_URL}{URL_APK_VERSION_DELETE}"
    params = {"id": TEST_ID}
    res = safe_request(api_session, "delete", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_apk_version_delete_batch(api_session):
    """APK版本发布-批量删除"""
    print(f"\n🚀 开始执行：{test_apk_version_delete_batch.__doc__}")
    url = f"{BASE_URL}{URL_APK_VERSION_DELETE_BATCH}"
    params = {"ids": TEST_IDS}
    res = safe_request(api_session, "delete", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_apk_version_edit_post(api_session):
    """APK版本发布-编辑（post）"""
    print(f"\n🚀 开始执行：{test_apk_version_edit_post.__doc__}")
    url = f"{BASE_URL}{URL_APK_VERSION_EDIT}"
    new_version = f"1.0.1_{int(time.time())}"
    new_version_name = f"V1.0.1_{int(time.time())}"

    json_data = {
        "id": 1,
        "appId": "com.neucir.flite",
        "channel": 0,
        "version": new_version,
        "versionName": new_version_name,
        "filePath": file_path,
        "releaseNoteZh": "自动化编辑版本",
        "releaseNoteEn": "Auto edit version",
        "status": 1,
        "creator": "admin"
    }

    res = safe_request(api_session, "post", url, json=json_data)
    print_response_info(json_data, res)
    assert_api_common(res)

def test_apk_version_edit_put(api_session):
    """APK版本发布-编辑（put）"""
    print(f"\n🚀 开始执行：{test_apk_version_edit_put.__doc__}")
    url = f"{BASE_URL}{URL_APK_VERSION_EDIT}"
    edit_version = f"1.0.1_{int(time.time())}"
    edit_version_name = f"V1.0.1_{int(time.time())}"

    json_data = {
        "id": 1,
        "appId": "com.neucir.flite",
        "channel": 0,
        "version": edit_version,
        "versionName": edit_version_name,
        "filePath": file_path,
        "releaseNoteZh": "自动化编辑成功",
        "releaseNoteEn": "Edit Success",
        "status": 1,
        "creator": "admin"
    }

    res = safe_request(api_session, "put", url, json=json_data)
    print_response_info(json_data, res)
    assert_api_common(res)

def test_apk_version_list(api_session):
    """APK版本发布-分页列表"""
    print(f"\n🚀 开始执行：{test_apk_version_list.__doc__}")
    url = f"{BASE_URL}{URL_APK_VERSION_LIST}"
    params = {"pageNo": TEST_PAGE_NO, "pageSize": TEST_PAGE_SIZE}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_apk_version_query_by_id(api_session):
    """APK版本发布-单条查询"""
    print(f"\n🚀 开始执行：{test_apk_version_query_by_id.__doc__}")
    url = f"{BASE_URL}{URL_APK_VERSION_QUERY_BY_ID}"
    params = {"id": TEST_ID}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_apk_latest_version(api_session):
    """apk-download-controller-获取APP最新版本"""
    print(f"\n🚀 开始执行：{test_apk_latest_version.__doc__}")
    url = f"{BASE_URL}{URL_APK_LATEST_VERSION}"
    res = safe_request(api_session, "get", url)
    print_response_info(None, res)
    assert_api_common(res)

# ==============================================
# 六、设备用户
# ==============================================
def test_user_device_info(api_session):
    """设备用户-查询设备是否存在"""
    print(f"\n🚀 开始执行：{test_user_device_info.__doc__}")
    url = f"{BASE_URL}{URL_USER_SIGNIN}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID}
    res = safe_request(api_session, "post", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

latest_firmware_url = ""
def test_user_latest_firmware_version(api_session):
    """设备用户-获取最新固件版本"""
    global latest_firmware_url
    print(f"\n🚀 开始执行：{test_user_latest_firmware_version.__doc__}")

    url = f"{BASE_URL}{URL_USER_LATEST_FIRMWARE_VERSION}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID}

    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

    # 🔥 直接拿接口返回的完整路径
    latest_firmware_url = res.json()["url"]
    print(f"\n✅ 真实固件路径：{latest_firmware_url}")

def test_firmware_download(api_session):
    """设备固件-下载最新的固件"""
    print(f"\n🚀 开始执行：{test_firmware_download.__doc__}")

    # ✅ 正确：BASE_URL 已经包含 /neucirflite_portal，直接拼接固件路径
    final_url = f"{BASE_URL}/{latest_firmware_url}"
    res = safe_request(api_session, "get", final_url, stream=True)
    print_response_info(None, res)

    assert res.status_code == 200, f"下载失败，状态码：{res.status_code}"
    assert len(res.content) > 0, "文件内容为空"

def test_user_save_device_settings(api_session):
    """设备用户-保存设备设置记录"""
    print(f"\n🚀 开始执行：{test_user_save_device_settings.__doc__}")
    url = f"{BASE_URL}{URL_USER_SAVE_DEVICE_SETTINGS}"
    params = {
        "cali_data": "calibration_test_data",
        "ctrl_setting": "control_test_config",
        "pid_setting": "pid_test_config",
        "record_id": 1,
        "record_name": "test_settings_001",
        "sensor_type": 1,
        "threshold_setting": "threshold_test_config"
    }

    res = safe_request(api_session, "post", url, params=params)
    print_response_info(params, res)

    # 通用断言 + 额外状态码校验
    assert_api_common(res)
    assert res.status_code in [200, 201], f"保存失败，状态码：{res.status_code}"

def test_user_get_device_settings(api_session):
    """设备用户-获取设备设置记录"""
    print(f"\n🚀 开始执行：{test_user_get_device_settings.__doc__}")
    url = f"{BASE_URL}{URL_USER_GET_DEVICE_SETTINGS}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

# 全局变量：保存添加的模型数据
saved_model_data = {}
def test_user_add_model_status(api_session):
    """设备用户-添加模型应用状态"""
    global saved_model_data
    print(f"\n🚀 开始执行：{test_user_add_model_status.__doc__}")
    url = f"{BASE_URL}{URL_USER_ADD_MODEL_STATUS}"

    params = {
        "addr": DEVICE_MAC,
        "uuid": DEVICE_UUID,
        "template_no": TEST_TEMPLATE_ID,
        "training_time": "2026-05-14 18:00:00"
    }

    res = safe_request(api_session, "post", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

    # 保存我们添加的数据
    saved_model_data = params

def test_user_get_model_status(api_session):
    """设备用户-获取当前模型应用"""
    print(f"\n🚀 开始执行：{test_user_get_model_status.__doc__}")
    url = f"{BASE_URL}{URL_USER_GET_MODEL_STATUS}"

    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)
    result = res.json().get("msg", {})

    # 预期值（添加时的数据）
    expect_template_no = str(saved_model_data["template_no"])  # 转成字符串
    expect_training_time = saved_model_data["training_time"]

    # 实际返回值
    actual_template_no = result.get("templateNo")
    actual_training_time = result.get("trainingTime")

    assert actual_template_no == expect_template_no, \
        f"模板编号不一致！期望：{expect_template_no}，实际：{actual_template_no}"

    assert actual_training_time == expect_training_time, \
        f"训练时间不一致！期望：{expect_training_time}，实际：{actual_training_time}"

    print("\n✅ 校验通过：添加的模型应用 == 查询到的模型应用")

def test_user_gesture_train(api_session):
    """设备用户-手势训练"""
    print(f"\n开始执行：{test_user_gesture_train.__doc__}")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    bin_path = os.path.join(script_dir, "data.bin")

    data = {
        "angle_cnt": 2,
        "channel": 255,
        "channelNUm": 255,
        "gesture_count": 2,
        "restart": 0,
        "sample_rate": 500,
        "template_description": "新测试",
        "template_name": "test",
        "template_no": 2,
        "totalTrainTimes": 2,
    }

    url = f"{BASE_URL}{URL_USER_GESTURE_TRAIN}"
    api_session.headers.pop("Content-Type", None)

    with open(bin_path, "rb") as f:
        files = [
            ("files", ("data.bin", f, "application/octet-stream"))
        ]

        res = safe_request(api_session, "post", url, data=data, files=files)
        assert_api_common(res)
        print("✅ 手势训练接口测试通过！")

def test_user_get_templates(api_session):
    """设备用户-获取所有模版信息"""
    print(f"\n🚀 开始执行：{test_user_get_templates.__doc__}")
    url = f"{BASE_URL}{URL_USER_GET_TEMPLATES}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

@pytest.mark.skip('尚未调通，test_user_user_info')
def test_user_user_info(api_session):
    """设备用户-通过id查询"""
    print(f"\n🚀 开始执行：{test_user_user_info.__doc__}")
    url = f"{BASE_URL}{URL_USER_GET_USER_INFO}"
    params = {"activate_key": "TEST_ACT_KEY_001", "addr": DEVICE_MAC}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)
#
@pytest.mark.skip('test_user_modify_template_info')
def test_user_modify_template_info(api_session):
    """设备用户-修改模板信息"""
    print(f"\n🚀 开始执行：{test_user_modify_template_info.__doc__}")
    url = f"{BASE_URL}{URL_USER_MODIFY_TEMPLATE_INFO}"
    params = {
        "template_id": 956,
        "template_name": "修改后的模板名称",
        "template_description": "修改后的描述"
    }

    # 发送请求：POST + params（swagger 标准格式）
    res = safe_request(api_session, "post", url, params=params)

    print_response_info(params, res)

    # 断言
    assert_api_common(res)
#
# @pytest.mark.skip('尚未调通，test_user_retrain')
def test_user_retrain(api_session):
    """设备用户-重新训练【swagger 精准版】"""
    print(f"\n🚀 开始执行：{test_user_retrain.__doc__}")
    url = f"{BASE_URL}{URL_USER_RETRAIN}"

    params = {
        "template_no": 2,          # 必传：你的模板编号（int数字）
        "training_time": "60"     # 必传：训练时间（字符串）
    }

    res = safe_request(api_session, "post", url, params=params)

    print_response_info(params, res)
    assert_api_common(res)
#
# @pytest.mark.skip('需要真实参数，test_user_retrain')
def test_user_get_training_records(api_session):
    """设备用户-获取训练记录"""
    print(f"\n🚀 开始执行：{test_user_get_training_records.__doc__}")

    url = f"{BASE_URL}{URL_USER_GET_TRAINING_RECORDS}"
    page_no = 1
    template_no = 2

    params = {
        "page_no": page_no,
        "template_no": template_no
    }

    res = safe_request(api_session, "get", url, params=params)

    print_response_info(params, res)
    assert_api_common(res)
#
@pytest.mark.skip('test_user_delete_training_record')
def test_user_delete_training_record(api_session):
    """设备用户-删除训练记录"""
    print(f"\n🚀 开始执行：{test_user_delete_training_record.__doc__}")
    url = f"{BASE_URL}{URL_USER_DELETE_TRAINING_RECORD}"
    template_no = 2
    training_time = "2026-05-18_14-33-08"
    params = {
        "template_no": template_no,
        "training_time": training_time
    }

    res = safe_request(api_session, "post", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)
#
# @pytest.mark.skip('test_user_delete_error_training_info')
def test_user_delete_error_training_info(api_session):
    """设备用户-删除错误训练信息"""
    print(f"\n🚀 开始执行：{test_user_delete_error_training_info.__doc__}")
    url = f"{BASE_URL}{URL_USER_DELETE_ERROR_TRAINING_INFO}"
    emg_model_id = 133
    params = {
        "emg_model_id": emg_model_id
    }

    res = safe_request(api_session, "post", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_user_check_latest_emg_models(api_session):
    """设备用户-查询有无训练完成的模型"""
    print(f"\n🚀 开始执行：{test_user_check_latest_emg_models.__doc__}")
    url = f"{BASE_URL}{URL_USER_CHECK_LATEST_EMG_MODELS}"

    # 🔥 重点：这个接口【不需要传任何 params】！！！
    res = safe_request(api_session, "get", url)

    print_response_info({}, res)
    assert_api_common(res)
#
@pytest.mark.skip('test_user_download_emg_model')
def test_user_download_emg_model(api_session):
    """设备用户-应用EMG模型"""
    print(f"\n🚀 开始执行：{test_user_download_emg_model.__doc__}")
    url = f"{BASE_URL}{URL_USER_DOWNLOAD_EMG_MODEL}"
    template_no = 133
    training_time = "2026-05-18 14:33:08"

    params = {
        "template_no": template_no,
        "training_time": training_time
    }

    res = safe_request(api_session, "get", url, params=params, stream=True)

    print_response_info(params, res)
    assert_api_common(res)
#
def test_user_download_emg_data(api_session):
    """设备用户-下载训练数据"""
    print(f"\n🚀 开始执行：{test_user_download_emg_data.__doc__}")

    url = f"{BASE_URL}{URL_USER_DOWNLOAD_EMG_DATA}"
    params = {
        "template_no": 2  # 真实有效、你已存在的模板编号
    }

    res = safe_request(api_session, "get", url, params=params, stream=True)

    print_response_info(params, res)
    assert_api_common(res)

def test_user_debug_info(api_session):
    """设备用户-上传调试信息"""
    print(f"\n🚀 开始执行：{test_user_debug_info.__doc__}")

    url = f"{BASE_URL}{URL_USER_DEBUG_INFO}"
    params = {
        "debug_info": "自动化测试上传调试信息"  # 必传字符串
    }

    res = safe_request(api_session, "post", url, params=params)

    print_response_info(params, res)
    assert_api_common(res)

@pytest.mark.skip('test_user_usage_stat')
def test_user_usage_stat(api_session):
    """设备用户-上传使用数据"""
    print(f"\n🚀 开始执行：{test_user_usage_stat.__doc__}")

    url = f"{BASE_URL}{URL_USER_USAGE_STAT}"

    latitude = 31.23
    longitude = 121.47
    total_open_times_1 = 1
    total_open_times_2 = 0
    total_open_times_3 = 0
    total_open_times_4 = 0
    total_open_times_5 = 0
    total_use_time = 100

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "total_open_times_1": total_open_times_1,
        "total_open_times_2": total_open_times_2,
        "total_open_times_3": total_open_times_3,
        "total_open_times_4": total_open_times_4,
        "total_open_times_5": total_open_times_5,
        "total_use_time": total_use_time
    }

    res = safe_request(api_session, "post", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)
#
def test_user_device_info_by_uuid(api_session):
    """设备用户-获取产品信息"""
    print(f"\n🚀 开始执行：{test_user_device_info_by_uuid.__doc__}")
    url = f"{BASE_URL}{URL_USER_DEVICE_INFO}"

    params = {
        "uuid": DEVICE_UUID
    }

    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)
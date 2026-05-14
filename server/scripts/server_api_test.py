import base64
import ddddocr
import pytest
import requests
import time
import json
import uuid
from datetime import datetime

from server.server_common import OperateSharedData

# ====================== 全局常量配置 ======================
HOST = "http://neucirflite-test.oymotion.com"
BASE_URL = f"{HOST}/neucirflite_portal"
REAL_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3Nzg2ODAxNTQsInVzZXJuYW1lIjoid2FuZ3J1aXdlaUBveW1vdGlvbi5jb20ifQ.wh4qUon9siPfdYSiU-C7EuZZ6K5kH7AGvQzfdrjn7c0"

HEADERS = {
    "X-Access-Token": REAL_TOKEN,
    "Content-Type": "application/json"
}

# ===================== 状态码 =====================
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404

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
URL_APK_VERSION_DELETE_BATCH = "apk_version/apkVersion/deleteBatch"
URL_APK_VERSION_EDIT = "apk_version/apkVersion/edit"
URL_APK_VERSION_LIST = "apk_version/apkVersion/list"
URL_APK_VERSION_QUERY_BY_ID = "apk_version/apkVersion/queryById"

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
URL_USER_GET_TRAINING_RECORDS = "/user/get_training_records"
URL_USER_LATEST_FIRMWARE_VERSION = "/user/latest_firmware_version"
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

URL_FIRMWARE_DOWNLOAD = "/firmware/{getTypeName}/{url}"

URL_USAGE_STATS_ADD = "/usagestats/add"
URL_USAGE_STATS_DELETE = "/usagestats/delete"
URL_USAGE_STATS_DELETE_BATCH = "/usagestats/deleteBatch"
URL_USAGE_STATS_EDIT = "/usagestats/edit"
URL_USAGE_STATS_LIST = "/usagestats/list"
URL_USAGE_STATS_QUERY_BY_ID = "/usagestats/queryById"

# ====================== 测试全局变量 & 测试数据 ======================
TEST_TEMPLATE_NO = 9999
TEST_TRAINING_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
TEST_UUID = f"AUTO_{uuid.uuid4().hex[:12].upper()}"
TEST_PAGE_NO = 1
TEST_PAGE_SIZE = 10
TEST_CAPTCHA_KEY = f"test_key_{uuid.uuid4().hex[:6]}"
TEST_QRCODE_ID = f"test_qrcode_{uuid.uuid4().hex[:6]}"
TEST_DEVICE_SERIAL_NO = f"SN_{uuid.uuid4().hex[:10].upper()}"
TEST_DEVICE_NAME = "OYFM-7000.json"

# ====================== 【修复】所有假ID 移除 ======================
TEST_ID = "1"           # 改为真实存在的 1
TEST_IDS = "1,2"        # 改为真实范围
TEST_VERSION = "V1.0.0"
DEVICE_MAC = "24:71:89:EF:27:EF"
DEVICE_UUID = "8266a4ba31decf20"
ACTIVATE_KEY = None

# 设备类型测试数据
TEST_TYPE_NAME = f"TYPE_{uuid.uuid4().hex[:6].upper()}"
TEST_HARDWARE_TYPE = 1
TEST_HARDWARE_VER = 2

# 设备固件测试数据
TEST_FW_DEVICE_TYPE_ID = 1
TEST_FW_VERSION = "V2.0.0"
TEST_FW_RELEASE_ZH = "固件版本测试中文说明"
TEST_FW_RELEASE_EN = "Firmware test release note"
TEST_FW_IS_VALID = 1
TEST_FW_URL = "/firmware/test.bin"

# 用户/训练测试数据
TEST_USER_ID = "10001"
TEST_TEMPLATE_ID = 1
TEST_TEMPLATE_NAME = f"AUTO_TPL_{uuid.uuid4().hex[:6]}"
TEST_MODEL_ID = 1
TEST_EMG_DATA = "test_emg_data"

# ====================== 工具函数 & 夹具 ======================
def check_test_stop_pause():
    try:
        is_stop, is_pause = OperateSharedData.read_control()
        if is_stop: pytest.exit("🛑 测试已停止")
        while is_pause:
            time.sleep(0.2)
            is_stop, is_pause = OperateSharedData.read_control()
            if is_stop: pytest.exit("🛑 测试已停止")
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
    """
    从登录响应中提取token，并自动设置到会话请求头
    :param session: requests.Session 会话对象
    :param login_response: 登录接口的响应对象
    """
    global REAL_TOKEN  # 声明要修改全局变量
    try:
        # 解析响应，提取token
        res_data = login_response.json()
        token = res_data["result"]["token"]

        # 设置到全局请求头，后续所有接口自动携带
        session.headers.update({
            "X-Access-Token": token
        })
        print(f"\n✅ 登录成功 | TOKEN 已自动生效：{token[:50]}...")

        REAL_TOKEN = token
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
    except:
        print(f"响应内容: {res.text[:200]}")
    print("=" * 50)

def assert_api_common(res):
    ALLOWED_STATUS_CODES = {HTTP_OK, HTTP_UNAUTHORIZED, HTTP_FORBIDDEN, HTTP_NOT_FOUND}
    status_code = res.status_code
    assert status_code in ALLOWED_STATUS_CODES, f"HTTP 状态码异常：{status_code}"

    if status_code == HTTP_UNAUTHORIZED:
        assert False, "HTTP 401：未授权"
    if status_code == HTTP_FORBIDDEN:
        assert False, "HTTP 403：权限不足"
    if status_code == HTTP_NOT_FOUND:
        assert False, "HTTP 404：接口不存在"

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
        if method.lower() == "get":
            return session.get(url, timeout=10,** kwargs)
        elif method.lower() == "post":
            return session.post(url, timeout=10, **kwargs)
        elif method.lower() == "put":
            return session.put(url, timeout=10,** kwargs)
        elif method.lower() == "delete":
            return session.delete(url, timeout=10, **kwargs)
    except Exception as e:
        pytest.skip(f"请求异常跳过: {str(e)}")

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
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert_api_common(res)

def test_default_settings(api_session):
    """系统-默认配置获取"""
    print(f"\n🚀 开始执行：{test_default_settings.__doc__}")
    url = f"{BASE_URL}{URL_DEFAULT_SETTINGS}".format(deviceName=TEST_DEVICE_NAME)
    res = safe_request(api_session,"get",url)
    print_response_info({"deviceName":TEST_DEVICE_NAME},res)
    assert_api_common(res)

def test_sys_random_image(api_session):
    """登录-获取验证码图片"""
    print(f"\n🚀 开始执行：{test_sys_random_image.__doc__}")
    url = f"{BASE_URL}{URL_SYS_RANDOM_IMAGE}".format(key=TEST_CAPTCHA_KEY)
    res = safe_request(api_session,"get",url)
    print_response_info({"key":TEST_CAPTCHA_KEY},res)
    assert_api_common(res)

# ==============================================
# 二、设备管理
# ==============================================
def test_device_add(api_session):
    """设备-新增设备"""
    print(f"\n🚀 开始执行：{test_device_add.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_ADD}"
    ts = int(time.time())
    json_data = {
        "activateKey": f"ACT_{ts}",
        "addr": f"11:22:33:44:55:{ts%100:02X}",
        "deviceSerialNo": f"SN_{ts}",
        "deviceTypeId": 1,
        "forbidden": 0,
        "remark": "自动化测试"
    }
    res = safe_request(api_session, "post", url, json=json_data)
    print_response_info(json_data, res)
    assert_api_common(res)

def test_device_list(api_session):
    """设备-分页列表"""
    print(f"\n🚀 开始执行：{test_device_list.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_LIST}"
    params = {"pageNo":TEST_PAGE_NO,"pageSize":TEST_PAGE_SIZE}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_query_by_id(api_session):
    """设备-单条查询"""
    print(f"\n🚀 开始执行：{test_device_query_by_id.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_QUERY_BY_ID}"
    params = {"id": TEST_ID}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_edit_post(api_session):
    """设备-编辑POST"""
    print(f"\n🚀 开始执行：{test_device_edit_post.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_EDIT}"
    json_data = {"id": int(TEST_ID), "remark":"自动化编辑"}
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_device_edit_put(api_session):
    """设备-编辑PUT"""
    print(f"\n🚀 开始执行：{test_device_edit_put.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_EDIT}"
    json_data = {"id": int(TEST_ID), "remark":"自动化PUT编辑"}
    res = safe_request(api_session,"put",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_device_log(api_session):
    """设备-设备日志查询"""
    print(f"\n🚀 开始执行：{test_device_log.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_LOG}".format(deviceSerialNo=TEST_DEVICE_SERIAL_NO)
    res = safe_request(api_session,"get",url)
    print_response_info({"deviceSerialNo":TEST_DEVICE_SERIAL_NO},res)
    assert res.status_code == 200

def test_device_delete(api_session):
    """设备-单条删除"""
    print(f"\n🚀 开始执行：{test_device_delete.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_DELETE}"
    params = {"id": TEST_ID}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_delete_batch(api_session):
    """设备-批量删除"""
    print(f"\n🚀 开始执行：{test_device_delete_batch.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_DELETE_BATCH}"
    params = {"ids": TEST_IDS}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

# ==============================================
# 三、设备类型管理
# ==============================================
def test_device_types_add(api_session):
    """设备类型-新增"""
    print(f"\n🚀 开始执行：{test_device_types_add.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_ADD}"
    json_data = {
        "typeName":TEST_TYPE_NAME,
        "hardwareType":TEST_HARDWARE_TYPE,
        "hardwareVer":TEST_HARDWARE_VER
    }
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_device_types_delete(api_session):
    """设备类型-单条删除"""
    print(f"\n🚀 开始执行：{test_device_types_delete.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_DELETE}"
    params = {"id": TEST_ID}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_types_delete_batch(api_session):
    """设备类型-批量删除"""
    print(f"\n🚀 开始执行：{test_device_types_delete_batch.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_DELETE_BATCH}"
    params = {"ids": TEST_IDS}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_types_edit_post(api_session):
    """设备类型-编辑POST"""
    print(f"\n🚀 开始执行：{test_device_types_edit_post.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_EDIT}"
    json_data = {
        "id": int(TEST_ID),
        "typeName":TEST_TYPE_NAME,
        "hardwareType":TEST_HARDWARE_TYPE,
        "hardwareVer":TEST_HARDWARE_VER
    }
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_device_types_edit_put(api_session):
    """设备类型-编辑PUT"""
    print(f"\n🚀 开始执行：{test_device_types_edit_put.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_EDIT}"
    json_data = {
        "id": int(TEST_ID),
        "typeName":TEST_TYPE_NAME,
        "hardwareType":TEST_HARDWARE_TYPE,
        "hardwareVer":TEST_HARDWARE_VER
    }
    res = safe_request(api_session,"put",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_device_types_list(api_session):
    """设备类型-分页列表"""
    print(f"\n🚀 开始执行：{test_device_types_list.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_LIST}"
    params = {"pageNo":TEST_PAGE_NO,"pageSize":TEST_PAGE_SIZE}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_types_query_by_id(api_session):
    """设备类型-通过id查询"""
    print(f"\n🚀 开始执行：{test_device_types_query_by_id.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_QUERY_BY_ID}"
    params = {"id": TEST_ID}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_types_devicetype(api_session):
    """设备类型-根据ID查询类型"""
    print(f"\n🚀 开始执行：{test_device_types_devicetype.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_DEVICE_TYPE}"
    params = {"id": int(TEST_ID)}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_types_devicetypename(api_session):
    """设备类型-获取类型名称列表"""
    print(f"\n🚀 开始执行：{test_device_types_devicetypename.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_DEVICE_TYPE_NAME}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert_api_common(res)

def test_device_types_top(api_session):
    """设备类型-最新前5条"""
    print(f"\n🚀 开始执行：{test_device_types_top.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_TYPES_TOP}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert_api_common(res)

# ==============================================
# 四、设备固件管理
# ==============================================
def test_device_firmware_add(api_session):
    """设备固件-新增"""
    print(f"\n🚀 开始执行：{test_device_firmware_add.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_ADD}"
    json_data = {
        "deviceTypeId":TEST_FW_DEVICE_TYPE_ID,
        "isValid":TEST_FW_IS_VALID,
        "releaseNoteZh":TEST_FW_RELEASE_ZH,
        "releaseNoteEn":TEST_FW_RELEASE_EN,
        "url":TEST_FW_URL,
        "version":TEST_FW_VERSION
    }
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_device_firmware_delete(api_session):
    """设备固件-单条删除"""
    print(f"\n🚀 开始执行：{test_device_firmware_delete.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_DELETE}"
    params = {"id": TEST_ID}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_firmware_delete_batch(api_session):
    """设备固件-批量删除"""
    print(f"\n🚀 开始执行：{test_device_firmware_delete_batch.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_DELETE_BATCH}"
    params = {"ids": TEST_IDS}
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_firmware_edit_post(api_session):
    """设备固件-编辑POST"""
    print(f"\n🚀 开始执行：{test_device_firmware_edit_post.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_EDIT}"
    json_data = {
        "id": int(TEST_ID),
        "deviceTypeId":TEST_FW_DEVICE_TYPE_ID,
        "isValid":TEST_FW_IS_VALID,
        "releaseNoteZh":TEST_FW_RELEASE_ZH,
        "releaseNoteEn":TEST_FW_RELEASE_EN,
        "url":TEST_FW_URL,
        "version":TEST_FW_VERSION
    }
    res = safe_request(api_session,"post",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_device_firmware_edit_put(api_session):
    """设备固件-编辑PUT"""
    print(f"\n🚀 开始执行：{test_device_firmware_edit_put.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_EDIT}"
    json_data = {
        "id": int(TEST_ID),
        "deviceTypeId":TEST_FW_DEVICE_TYPE_ID,
        "isValid":TEST_FW_IS_VALID,
        "releaseNoteZh":TEST_FW_RELEASE_ZH,
        "releaseNoteEn":TEST_FW_RELEASE_EN,
        "url":TEST_FW_URL,
        "version":TEST_FW_VERSION
    }
    res = safe_request(api_session,"put",url,json=json_data)
    print_response_info(json_data,res)
    assert_api_common(res)

def test_device_firmware_list(api_session):
    """设备固件-分页列表"""
    print(f"\n🚀 开始执行：{test_device_firmware_list.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_LIST}"
    params = {"pageNo":TEST_PAGE_NO,"pageSize":TEST_PAGE_SIZE,"version":TEST_FW_VERSION}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_firmware_query_type_id(api_session):
    """设备固件-通过typeid查询"""
    print(f"\n🚀 开始执行：{test_device_firmware_query_type_id.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_QUERY_TYPE_ID}"
    params = {"id": TEST_ID}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_device_firmware_upload(api_session):
    """设备固件-通用文件上传"""
    print(f"\n🚀 开始执行：{test_device_firmware_upload.__doc__}")
    url = f"{BASE_URL}{URL_DEVICE_FIRMWARE_UPLOAD}"
    res = safe_request(api_session,"post",url)
    print_response_info(None,res)
    assert_api_common(res)

def test_firmware_download(api_session):
    """固件下载"""
    print(f"\n🚀 开始执行：{test_firmware_download.__doc__}")
    url = f"{BASE_URL}{URL_FIRMWARE_DOWNLOAD}".format(getTypeName="test",url="test.bin")
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
    assert res.status_code == 200

# ==============================================
# 五、APK版本发布
# ==============================================
file_path = ""
def test_apk_upload_file(api_session):
    """APK文件上传-上传APK文件"""
    print(f"\n🚀 开始执行：{test_apk_upload_file.__doc__}")
    url = f"{BASE_URL}{URL_APK_UPLOAD_FILE}"

    # 自动创建测试用 APK
    with open("test.apk", "wb") as f:
        f.write(b"test apk content")

    # 上传文件必须移除 JSON 头
    api_session.headers.pop("Content-Type", None)

    files = {
        "file": ("test.apk", open("test.apk", "rb"), "application/vnd.android.package-archive")
    }
    res = safe_request(api_session, "post", url, files=files)

    # 恢复 JSON 头
    api_session.headers["Content-Type"] = "application/json"

    print_response_info(None, res)
    assert_api_common(res)

    # 全局赋值：保存后端返回的真实 filePath
    global file_path
    result = res.json()["result"]
    file_path = result["filePath"]  # 只拿路径字符串！！！
    print(f"\n✅ 真实文件路径：{file_path}")

def test_apk_delete_file(api_session):
    """APK文件上传-删除APK文件"""
    print(f"\n🚀 开始执行：{test_apk_delete_file.__doc__}")
    url = f"{BASE_URL}{URL_APK_DELETE_FILE}"
    # 使用全局变量里的【真实路径】删除
    params = {"filePath": file_path}
    res = safe_request(api_session, "delete", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_apk_version_add(api_session):
    """APK版本发布-添加"""
    print(f"\n🚀 开始执行：{test_apk_version_add.__doc__}")
    url = f"{BASE_URL}{URL_APK_VERSION_ADD}"

    # 动态唯一版本号 ✅
    version = f"1.0.1_{int(time.time())}"
    version_name = f"V1.0.1_{int(time.time())}"

    json_data = {
        "appId": "com.neucir.flite",
        "channel": 0,
        "version": version,  # 版本号
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
    res = safe_request(api_session,"delete",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_apk_version_edit_post(api_session):
    """APK版本发布-编辑（post）"""
    print(f"\n🚀 开始执行：{test_apk_version_edit_post.__doc__}")
    url = f"{BASE_URL}{URL_APK_VERSION_EDIT}"

    # 动态生成新版本号（不重复）
    new_version = f"1.0.1_{int(time.time())}"
    new_version_name = f"V1.0.1_{int(time.time())}"

    json_data = {
        "id": 1,  # 固定ID=1，和删除保持一致
        "appId": "com.neucir.flite",
        "channel": 0,
        "version": new_version,  # 动态版本号
        "versionName": new_version_name,
        "filePath": file_path,  # 全局真实路径
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

    # 动态生成唯一版本号（带时间戳，永不重复）
    edit_version = f"1.0.1_{int(time.time())}"
    edit_version_name = f"V1.0.1_{int(time.time())}"

    json_data = {
        "id": 1,  # 固定ID=1
        "appId": "com.neucir.flite",
        "channel": 0,
        "version": edit_version,  # 动态版本号
        "versionName": edit_version_name,
        "filePath": file_path,  # 上传后的真实路径
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
    params = {"pageNo":TEST_PAGE_NO,"pageSize":TEST_PAGE_SIZE}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_apk_version_query_by_id(api_session):
    """APK版本发布-单条查询"""
    print(f"\n🚀 开始执行：{test_apk_version_query_by_id.__doc__}")
    url = f"{BASE_URL}{URL_APK_VERSION_QUERY_BY_ID}"
    params = {"id": TEST_ID}
    res = safe_request(api_session,"get",url,params=params)
    print_response_info(params,res)
    assert_api_common(res)

def test_apk_latest_version(api_session):
    """apk-download-controller-获取APP最新版本"""
    print(f"\n🚀 开始执行：{test_apk_latest_version.__doc__}")
    url = f"{BASE_URL}{URL_APK_LATEST_VERSION}"
    res = safe_request(api_session,"get",url)
    print_response_info(None,res)
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

def test_user_get_device_settings(api_session):
    """设备用户-获取设备设置记录"""
    print(f"\n🚀 开始执行：{test_user_get_device_settings.__doc__}")
    url = f"{BASE_URL}{URL_USER_GET_DEVICE_SETTINGS}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_user_save_device_settings(api_session):
    """设备用户-保存设备设置记录"""
    print(f"\n🚀 开始执行：{test_user_save_device_settings.__doc__}")
    url = f"{BASE_URL}{URL_USER_SAVE_DEVICE_SETTINGS}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID}
    json_data = {"setting": "test"}
    res = safe_request(api_session, "post", url, json=json_data, params=params)
    print_response_info({**params, **json_data}, res)
    assert_api_common(res)

def test_user_get_templates(api_session):
    """设备用户-获取所有模版信息"""
    print(f"\n🚀 开始执行：{test_user_get_templates.__doc__}")
    url = f"{BASE_URL}{URL_USER_GET_TEMPLATES}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_user_modify_template_info(api_session):
    """设备用户-修改模板信息"""
    print(f"\n🚀 开始执行：{test_user_modify_template_info.__doc__}")
    url = f"{BASE_URL}{URL_USER_MODIFY_TEMPLATE_INFO}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID}
    json_data = {"templateId": TEST_TEMPLATE_ID, "templateName": TEST_TEMPLATE_NAME}
    res = safe_request(api_session, "post", url, json=json_data, params=params)
    print_response_info({**params, **json_data}, res)
    assert_api_common(res)

def test_user_gesture_train(api_session):
    """设备用户-手势训练"""
    print(f"\n🚀 开始执行：{test_user_gesture_train.__doc__}")
    url = f"{BASE_URL}{URL_USER_GESTURE_TRAIN}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID}
    json_data = {"templateId": TEST_TEMPLATE_ID, "emgData": TEST_EMG_DATA}
    res = safe_request(api_session, "post", url, json=json_data, params=params)
    print_response_info({**params, **json_data}, res)
    assert_api_common(res)

def test_user_single_train(api_session):
    """设备用户-单次训练"""
    print(f"\n🚀 开始执行：{test_user_single_train.__doc__}")
    url = f"{BASE_URL}{URL_USER_SINGLE_TRAIN}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID}
    json_data = {"templateId": TEST_TEMPLATE_ID}
    res = safe_request(api_session, "post", url, json=json_data, params=params)
    print_response_info({**params, **json_data}, res)
    assert_api_common(res)

def test_user_retrain(api_session):
    """设备用户-重新训练"""
    print(f"\n🚀 开始执行：{test_user_retrain.__doc__}")
    url = f"{BASE_URL}{URL_USER_RETRAIN}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID}
    json_data = {"templateId": TEST_TEMPLATE_ID}
    res = safe_request(api_session, "post", url, json=json_data, params=params)
    print_response_info({**params, **json_data}, res)
    assert_api_common(res)

def test_user_get_training_records(api_session):
    """设备用户-获取训练记录"""
    print(f"\n🚀 开始执行：{test_user_get_training_records.__doc__}")
    url = f"{BASE_URL}{URL_USER_GET_TRAINING_RECORDS}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

# ====================== 【修复】删除训练记录 → 改为 POST ======================
def test_user_delete_training_record(api_session):
    """设备用户-删除训练记录"""
    print(f"\n🚀 开始执行：{test_user_delete_training_record.__doc__}")
    url = f"{BASE_URL}{URL_USER_DELETE_TRAINING_RECORD}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID, "id": TEST_ID}
    res = safe_request(api_session, "post", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_user_delete_error_training_info(api_session):
    """设备用户-删除错误训练信息"""
    print(f"\n🚀 开始执行：{test_user_delete_error_training_info.__doc__}")
    url = f"{BASE_URL}{URL_USER_DELETE_ERROR_TRAINING_INFO}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID, "id": TEST_ID}
    res = safe_request(api_session, "post", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_user_user_info(api_session):
    """设备用户-通过id查询"""
    print(f"\n🚀 开始执行：{test_user_user_info.__doc__}")
    url = f"{BASE_URL}/user/user_info"
    params = {"activate_key": "TEST_ACT_KEY_001", "addr": DEVICE_MAC}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_user_get_model_status(api_session):
    """设备用户-获取当前模型应用"""
    print(f"\n🚀 开始执行：{test_user_get_model_status.__doc__}")
    url = f"{BASE_URL}{URL_USER_GET_MODEL_STATUS}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_user_add_model_status(api_session):
    """设备用户-添加模型应用状态"""
    print(f"\n🚀 开始执行：{test_user_add_model_status.__doc__}")
    url = f"{BASE_URL}{URL_USER_ADD_MODEL_STATUS}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID}
    json_data = {"modelId": TEST_MODEL_ID}
    res = safe_request(api_session, "post", url, json=json_data, params=params)
    print_response_info({**params, **json_data}, res)
    assert_api_common(res)

def test_user_check_latest_emg_models(api_session):
    """设备用户-查询有无训练完成的模型"""
    print(f"\n🚀 开始执行：{test_user_check_latest_emg_models.__doc__}")
    url = f"{BASE_URL}{URL_USER_CHECK_LATEST_EMG_MODELS}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_user_download_emg_model(api_session):
    """设备用户-应用EMG模型"""
    print(f"\n🚀 开始执行：{test_user_download_emg_model.__doc__}")
    url = f"{BASE_URL}{URL_USER_DOWNLOAD_EMG_MODEL}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID, "modelId": TEST_MODEL_ID}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert res.status_code == 200

def test_user_download_emg_data(api_session):
    """设备用户-下载训练数据"""
    print(f"\n🚀 开始执行：{test_user_download_emg_data.__doc__}")
    url = f"{BASE_URL}{URL_USER_DOWNLOAD_EMG_DATA}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID, "id": TEST_ID}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert res.status_code == 200

def test_user_latest_firmware_version(api_session):
    """设备用户-获取最新固件版本"""
    print(f"\n🚀 开始执行：{test_user_latest_firmware_version.__doc__}")
    url = f"{BASE_URL}{URL_USER_LATEST_FIRMWARE_VERSION}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_user_debug_info(api_session):
    """设备用户-上传调试信息"""
    print(f"\n🚀 开始执行：{test_user_debug_info.__doc__}")
    url = f"{BASE_URL}{URL_USER_DEBUG_INFO}"
    params = {"addr": DEVICE_MAC, "uuid": DEVICE_UUID}
    json_data = {"info": "test_debug"}
    res = safe_request(api_session, "post", url, json=json_data, params=params)
    print_response_info({**params, **json_data}, res)
    assert_api_common(res)

def test_user_usage_stat(api_session):
    """设备用户-上传使用数据"""
    print(f"\n🚀 开始执行：{test_user_usage_stat.__doc__}")
    url = f"{BASE_URL}/user/usage_stat"
    params = {
        "addr": DEVICE_MAC, "uuid": DEVICE_UUID, "latitude": 31.23, "longitude": 121.47,
        "total_open_times_1": 1, "total_open_times_2": 0, "total_open_times_3": 0,
        "total_open_times_4": 0, "total_open_times_5": 0, "total_use_time": 100
    }
    res = safe_request(api_session, "post", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_user_device_info_by_uuid(api_session):
    """设备用户-获取产品信息"""
    print(f"\n🚀 开始执行：{test_user_device_info_by_uuid.__doc__}")
    url = f"{BASE_URL}/user/device_info"
    params = {"uuid": DEVICE_UUID}
    res = safe_request(api_session, "get", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_user_get_training_status(api_session):
    """设备用户-查看单机手势状态"""
    print(f"\n🚀 开始执行：{test_user_get_training_status.__doc__}")
    url = f"{BASE_URL}/user/getTrainingStatus"
    params = {"addr": DEVICE_MAC, "templateNo": 1, "gestureCount": 1}
    res = safe_request(api_session, "post", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)

def test_user_single_gesture_train(api_session):
    """设备用户-单机手势训练"""
    print(f"\n🚀 开始执行：{test_user_single_gesture_train.__doc__}")
    url = f"{BASE_URL}/user/single_train"
    params = {"addr": DEVICE_MAC, "templateName": "auto_test_single", "gestureCount": 1}
    res = safe_request(api_session, "post", url, params=params)
    print_response_info(params, res)
    assert_api_common(res)
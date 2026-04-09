import time
import pytest
import subprocess
import psutil

EXE_PATH = r"D:\Program Files\NeuroSync\Recorder3\NeuroSync.Client.Recorder.exe"
process = None


def test_start_app():
    """启动应用"""
    global process
    process = subprocess.Popen(EXE_PATH)
    time.sleep(3)
    assert process.poll() is None, "应用启动失败"


def test_stop_app():
    """关闭应用"""
    global process
    if process and process.poll() is None:
        # 安全关闭进程
        parent = psutil.Process(process.pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()

    time.sleep(3)
    assert process.poll() is not None, "应用未关闭"
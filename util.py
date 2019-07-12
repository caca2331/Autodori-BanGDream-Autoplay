import subprocess

# provides bridge to adb


def screenshot():
    subprocess.run(["adb", "shell", "screencap", "-p", "cap.png"])


# TODO: 确认从adb到手机的延迟
def move(x1, y1, x2, y2, duration):
    subprocess.run(["adb", "shell", "input", ""])


def touch(x, y):
    subprocess.run(["adb", "shell", "input", "tap", x, y])

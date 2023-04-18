import psutil
import time
from psychopy import core
import os, glob

def check_power_plugged():
    return battery.power_plugged if (battery := psutil.sensors_battery()) else True

def wait_until(clock, deadline, hogCPUperiod=0.1, keyboard_accuracy=.0005):
    if deadline < clock.getTime():
        print(f'ERROR: wait_until called after deadline: {deadline} < {clock.getTime()}')
    sleep_until = deadline - hogCPUperiod
    poll_windows()
    current_time = clock.getTime()
    while current_time < deadline:
        if current_time < sleep_until:
            time.sleep(keyboard_accuracy)
        poll_windows()
        current_time = clock.getTime()

def poll_windows():
    for winWeakRef in core.openWindows:
        win = winWeakRef()
        if (win.winType == "pyglet" and
                hasattr(win.winHandle, "dispatch_events")):
            win.winHandle.dispatch_events()  # pump events

def wait_until_yield(clock, deadline, hogCPUperiod=0.1, keyboard_accuracy=.0005):
    sleep_until = deadline - hogCPUperiod
    poll_windows()
    current_time = clock.getTime()
    while current_time < deadline:
        if current_time < sleep_until:
            time.sleep(keyboard_accuracy)
            yield False

        poll_windows()
        current_time = clock.getTime()

def get_subject_soundcheck_video(subject):
    setup_video_path = glob.glob(
        os.path.join(
            "data", "videos", "subject_setup_videos", f"sub-{subject}_*"
        )
    )
    return (
        setup_video_path[0]
        if len(setup_video_path)
        else os.path.join(
            "data",
            "videos",
            "subject_setup_videos",
            "sub-default_setup_video.mp4",
        )
    )

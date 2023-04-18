import os
import time
import argparse
import datetime
from src.shared import eyetracking

BASE_OUTPUT_DIR = '/home/basile/tests'

def start_eyetracker(args):

    output_path = f"{BASE_OUTPUT_DIR}/{parsed.study}/sub-{parsed.subject}{f'/ses-{parsed.session}' if parsed.session else ''}"
    os.makedirs(output_path, exist_ok=True)
    basename = f"pupil_{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    eyetracker_client = eyetracking.EyeTrackerClient(
        output_path=output_path,
        output_fname_base=basename,
        profile=False,
        debug=True,
    )

    eyetracker_client.send_recv_notification(
        {
            "subject": "start_plugin",
            "name": "ScreenMarkerChoreographyPlugin",
            "args": {
                "fullscreen": True,
                "marker_scale": 1.0,
                "sample_duration": 360,
                "monitor_name": "DP-2 [1]",
                "fixed_screen": True,
                "selected_gazer_class_name": "Gazer2D",
            },
        }
    )

    eyetracker_client.send_recv_notification(
        {
            "subject": "start_plugin",
            "name": "Annotation_Capture",
            "args": {
                "annotation_definitions": [['Trigger','T'], ['Trigger5','5'], ['Trigger%','%']]
            },
        }
    )


    #print("starting et client")
    #eyetracker_client.start()

    #eyetracker_client.join(5)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="main.py",
        description=("Run all tasks in a session"),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--study", "-p", required=True, help="Study name")
    parser.add_argument("--subject", "-s", required=True, help="Subject ID")
    parser.add_argument("--session", "-ss", help="Session")
    return parser.parse_args()

if __name__ == "__main__":
    parsed = parse_args()
    start_eyetracker(parsed)

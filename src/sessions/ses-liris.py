from ..tasks import video, task_base
import numpy as np


def get_videos(subject, session):
    video_idx = np.loadtxt(
        "data/liris/order_fmri_neuromod.csv", delimiter=",", skiprows=1, dtype=np.int
    )
    return video_idx[video_idx[:, 0] == session, subject + 1]


def get_tasks(parsed):

    tasks = []

    video_indices = get_videos(int(parsed.subject), int(parsed.session))

    tasks.extend(
        video.SingleVideo(
            f"data/liris/videos/{idx:03d}.mp4", name=f"task-liris{idx:03d}"
        )
        for idx in video_indices
    )
    return tasks

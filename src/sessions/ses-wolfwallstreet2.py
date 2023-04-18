from ..tasks import images, video, memory, task_base

TASKS = [
    video.SingleVideo(
        "data/videos/the_wolf_of_wall_street/the_wolf_of_wall_street_seg%02d.mkv"
        % seg_idx,
        aspect_ratio=12 / 5,
        name="the_wolf_of_wall_street_seg-%d" % seg_idx,
    )
    for seg_idx in range(7, 13)
]

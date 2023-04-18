from ..tasks import images, video, memory, task_base

TASKS = [
    video.SingleVideo(
        "data/videos/bourne_supremacy/bourne_supremacy_seg%02d.mkv" % seg_idx,
        aspect_ratio=372 / 157,
        name="bourne_supremacy_seg-%d" % seg_idx,
    )
    for seg_idx in range(6, 11)
]

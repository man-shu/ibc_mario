from ..tasks import images, video, memory, task_base

TASKS = [
    video.SingleVideo(
        "data/videos/hidden_figures/hidden_figures_seg%02d.mkv" % seg_idx,
        aspect_ratio=12 / 5,
        name="hidden_figures_seg-%d" % seg_idx,
    )
    for seg_idx in range(1, 7)
]

# 410 volumes each

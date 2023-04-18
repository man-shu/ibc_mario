from ..tasks import video

TASKS = []

for episode in range(1, 25):
    TASKS.extend(
        video.SingleVideo(
            "data/videos/friends/s2/friends_s2e%02d%s.mkv"
            % (episode, segment),
            aspect_ratio=4 / 3.0,
            name="task-friends-s2e%d%s" % (episode, segment),
        )
        for segment in "ab"
    )

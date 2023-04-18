from ..tasks import video

TASKS = []

for episode in range(1, 26):
    TASKS.extend(
        video.SingleVideo(
            "data/videos/friends/s3/friends_s3e%02d%s.mkv"
            % (episode, segment),
            aspect_ratio=4 / 3.0,
            name="task-friends-s3e%d%s" % (episode, segment),
        )
        for segment in "ab"
    )

import os
import random
import retro
import json

retro.data.Integrations.add_custom_path(
        os.path.join(os.getcwd(), "data", "videogames")
)

from ..tasks import images, videogame, memory, task_base

TASKS = [
    videogame.VideoGameMultiLevel(
        game_name='SpaceInvaders-Atari2600',
        state_names=["Start"],
        scenarii=['scenario'],
        repeat_scenario=True,
        max_duration=10 * 60,
        name="task-spaceinvaders",
        instruction="Let's play SpaceInvaders",
    )
]

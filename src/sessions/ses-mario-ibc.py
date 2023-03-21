import os
import random
import retro
import json

# point to a copy of the whole gym-retro with custom states and scenarii
retro.data.Integrations.add_custom_path(
        os.path.join(os.getcwd(), "data", "videogames", "mario")
)

from psychopy import logging
from ..tasks import videogame, task_base

from .game_questionnaires import flow_ratings

scenario = "scenario"

exclude_list = [(2,2),(7,2)] # all levels 4 are excluded below

def create_states(init_world, init_level):
    all_states = []
    init_world = int(init_world)
    init_level = int(init_level)
    if init_level > 1:
        while init_level < 4:
            world = init_world
            level = init_level
            state = f"Level{world}-{level}"
            all_states.append(state)
            init_level += 1
        init_world += 1
        init_level = 1
    for world in range(init_world, 9):
        for level in range(init_level, 4):
            state = f"Level{world}-{level}"
            all_states.append(state)
    return all_states

# code adaptive design for learning phase

def get_tasks(parsed):
    bids_sub = "sub-%s" % parsed.subject
    savestate_path = os.path.abspath(os.path.join(parsed.output, "sourcedata", bids_sub, f"{bids_sub}_task-mario_savestate.json"))
    last_run_time_up = False
    last_run_movie_path = None
    # check for a "savestate"
    if os.path.exists(savestate_path):
        with open(savestate_path) as f:
            savestate = json.load(f)
    else:
        savestate = {"world": 1, "level":1}

    all_states = create_states(savestate['world'], savestate['level'])

    for run in range(10):
        if savestate['world'] == 9:
            break
        if run==0:
            yield task_base.Pause(
                text="Appuyez sur A lorsque vous êtes prêt à continuer",
                pic_path="/home/himanshu/Desktop/IBC/cognitive_protocols/mario/instruction/controls_fr1.png",
                wait_key='a',
                text_pos=(0, 0.51)
            )
        # receive first ttl pulse and initiate stimulation
        yield task_base.Pause(
            text="+",
            wait_key='t', text_color='red', text_height=0.2
        )
        task = videogame.VideoGameMultiLevel(
            game_name='SuperMarioBros-Nes',
            state_names=all_states,
            scenarii=[scenario] * len(all_states),
            repeat_scenario=False,
            max_duration=20,  # if when level completed or dead we exceed that time in secs, stop the task
            name=f"task-mario_run-{run+1:02d}",
            instruction="jouer à Super Mario Bros {state_name} \n\n Let's-a go!",
            post_run_ratings = [(k, q, 7) for k, q in enumerate(flow_ratings)],
            use_eyetracking=True,
            time_exceeded=last_run_time_up,
            last_movie_path=last_run_movie_path,
            hard_run_duration_limit=True,
            show_instruction_between_repetitions=False
        )
        yield task
        if task.time_exceeded:
            logging.exp(f"Time up")
            last_run_time_up = True
            last_run_movie_path = task.stop_state_outfile
        else:
            print('Should never enter here')
            last_run_time_up = False
            last_run_movie_path = None

        splitted_state = task.state_name.split('-')
        savestate['level'] = splitted_state[1]
        savestate['world'] = splitted_state[0].split('Level')[1]

        with open(savestate_path, 'w') as f:
            json.dump(savestate, f)

        all_states = create_states(savestate['world'], savestate['level'])

        yield task_base.Pause(
            text="FIN",
            wait_key='space'
        )
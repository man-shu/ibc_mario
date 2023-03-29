"""
Event extraction script for mario.

Himanshu Aggarwal
himanshu.aggarwal@inria.fr
January 2023
"""
import pandas as pd
import os
import numpy as np
import retro
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, TextBox
from scipy.signal import convolve
import warnings
warnings.filterwarnings("ignore")


def take_input():
    while True:
        try:
            sub_num = int(input("Enter subject number: "))
            ses_num = int(input("Enter session number: "))
        except ValueError:
            print("Invalid input. Expecting integers.")
            continue
        else:
            break

    return sub_num, ses_num


def setup_io_files(sub_num, ses_num):
    path = os.getcwd()
    data_dir = os.path.join(path, 'output', 'sourcedata', f'sub-{sub_num}', f'ses-{ses_num}')
    data_files = sorted(os.listdir(data_dir))

    out_dir = os.path.join(path, 'output_paradigm_descriptors')
    try:
        os.mkdir(out_dir)
    except OSError:
        pass
    out_files = sorted(os.listdir(out_dir))

    practice = []
    main = []
    for file in data_files:
        if file.split('.')[-1] == 'tsv':
            if file.split('_')[0]=='pract':
                if int(file.split('_')[0].split('-')[1]) == sub_num:
                    practice.append(file)
            elif file.split('_')[0]=='par':
                continue
            else:
                if int(file.split('_')[0].split('-')[1]) == sub_num:
                    main.append(file)
    return data_dir, main, practice, out_dir, out_files


def check_presence(filename, list_of_files):
    if filename in list_of_files:
        count = 0
        for f in list_of_files:
            if f==filename:
                count+=1
        filename = filename.split('.')[0]+'('+str(count)+').'+filename.split('.')[1]
        return check_presence(filename,list_of_files)
    else:
        return filename
    
def load_movie(bk2):
    movie = retro.Movie(bk2)
    duration = -1
    while movie.step():
        duration += 1
    movie = retro.Movie(bk2)
    # movie.step()
    emulator = retro.make(game=movie.get_game(), state=retro.State.NONE, use_restricted_actions=retro.Actions.ALL, players=movie.players)
    data = movie.get_state()
    emulator.initial_state = data
    emulator.reset()
    return emulator, movie, duration

def create_frames(emulator, movie, video_delay=0):

    frame_imgs = []

    frames = 0
    score = [0] * movie.players

    while True:
        if movie.step():
            keys = []
            for p in range(movie.players):
                for i in range(emulator.num_buttons):
                    keys.append(movie.get_key(i, p))
        elif video_delay < 0 and frames < -video_delay:
            keys = [0] * emulator.num_buttons
        else:
            break
        display, reward, done, info = emulator.step(keys)
        if movie.players > 1:
            for p in range(movie.players):
                score[p] += reward[p]
        else:
            score[0] += reward
        frames += 1

        frame_imgs.append(emulator.__dict__['img'])

    frame_imgs_arr = np.stack(frame_imgs)

    return frame_imgs_arr

def plot_explorer(frames, info, labels, boolean):

    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    fig.subplots_adjust(bottom=0.25)


    im = axs[0].imshow(frames[0])

    for var, label in zip(info, labels):
        if not boolean:
            var.plot(ax=axs[1], label=label)
        else:
            axs[1].imshow(var, label=label)
        

    axs[1].set_title('All vars')
    axs[1].legend()

    # Create the RangeSlider
    slider_ax = fig.add_axes([0.20, 0.1, 0.60, 0.03])
    slider = Slider(slider_ax, "Frame", 0, len(info[0]), valstep=1)

    axbox = fig.add_axes([0.81, 0.1, 0.08, 0.04])
    text_box = TextBox(axbox, "", initial=0, textalignment="center")

    # Create the Vertical lines on the histogram
    upper_limit_line = axs[1].axvline(slider.val, color='k')

    def update(val):
        # The val passed to a callback by the RangeSlider will
        # be a tuple of (min, max)
        # Update the image's colormap
        t = int(val)

        axs[0].imshow(frames[t])

        # Update the position of the vertical lines
        upper_limit_line.set_xdata([t, t])
        text_box.eventson = False
        text_box.set_val(t)

        # Redraw the figure to ensure it updates
        # fig.canvas.draw_idle()
        fig.canvas.blit()
        text_box.eventson = True

    def submit(val):
        # The val passed to a callback by the RangeSlider will
        # be a tuple of (min, max)
        # Update the image's colormap
        t = int(val)

        axs[0].imshow(frames[t])

        # Update the position of the vertical lines
        upper_limit_line.set_xdata([t, t])
        slider.eventson = False
        slider.set_val(t)

        # Redraw the figure to ensure it updates
        # fig.canvas.draw_idle()
        fig.canvas.draw()
        slider.eventson = True

    slider.on_changed(update)
    text_box.on_submit(submit)

    plt.show()


def extract_events(file, data_dir, out_files, out_dir, do_convolve=False):
    file_path = os.path.join(data_dir, file)
    data = pd.read_csv(file_path, delimiter='\t')
    if len(data) == 0:
        print('Data file empty - {}'.format(file))
        # return 0
    else:
        components = file.split('_')

        task = components[-3]
        sub = components[0]
        run = components[-2]
        ses = components[1]

        run_bk2s = list(data[data['trial_type'] == 'gym-retro_game']['stim_file'])

        run_actions = []
        run_infos = []
        frame_imgs_arrs = []
        total_duration = 0
        for run_bk2 in run_bk2s:     
            # os.system(f'python play_session.py {run_bk2} -i -a >/dev/null 2>&1')
            os.system(f'python play_session.py {run_bk2} -i -a')

            emulator, movie, duration = load_movie(run_bk2)
            frame_imgs_arr = create_frames(emulator, movie, video_delay=0)
            frame_imgs_arrs.append(frame_imgs_arr)

            run_npz_filename = run_bk2.split('.')[0] + '.npz'
            run_npz = np.load(run_npz_filename, allow_pickle=True)
            run_action = pd.DataFrame(data=run_npz['actions'], columns=['keypress_runshoot', '_', '__', '___', 'keypress_up', 'keypress_down', 'keypress_left', 'keypress_right', 'keypress_jump'])
            run_action = run_action.drop(columns=['_', '__', '___'])
            run_info = {k: [d.get(k) for d in run_npz['info']] for k in set().union(*run_npz['info'])}
            run_info = pd.DataFrame(data=run_info)

            run_actions.append(run_action)
            run_infos.append(run_info)

            total_duration += duration

            emulator.close()

        frame_imgs_arrs = np.concatenate(frame_imgs_arrs)
        run_actions = pd.concat(run_actions)
        run_actions.reset_index(drop=True)
        run_infos = pd.concat(run_infos)
        run_infos = run_infos.reset_index(drop=True)

        # intermediate variables
        run_infos['score_increment'] = run_infos['score'].diff().fillna(0)
        run_infos['coin_increment'] = run_infos['coins'].diff().fillna(0)
        run_infos['invincible'] = np.where(run_infos['star_timer'] > 0, 5, 0)
        run_infos['player_state'] = run_infos['invincible'] + run_infos['player_state']
        run_infos['track_powerup_miss'] = run_infos['powerup_yes_no'] + run_infos['player_state']
        run_infos['track_powerup_miss'] = run_infos['track_powerup_miss'].diff().fillna(0)
        
        # save variables that define final relevant events
        relevant_events = ['reward_coin', 'reward_bricksmash', 'reward_enemykill_stomp', 'reward_enemykill_kick', 'reward_enemykill_impact', 'reward_powerup_taken', 'loss_powerup_miss', 'loss_powerdown', 'loss_dying', 'onscreen_enemy', 'onscreen_powerup', 'action_fire', 'action_leftwalk', 'action_leftrun', 'action_rightwalk', 'action_rightrun', 'action_rest', 'action_jump', 'action_climbingup', 'action_pipedown', 'action_crouch']

        # rewarding events
        if do_convolve:
            run_infos['reward_coin'] = convolve(run_infos['coin_increment'], np.ones(23), mode='same')
        else:
            run_infos['reward_coin'] = np.where(run_infos['coin_increment'] > 0, 1, 0)
        run_infos['reward_bricksmash'] = np.where((run_infos['score_increment'] == 5) & (run_infos['jump_airborne'] == 1), 1, 0)
        if do_convolve:
            run_infos['reward_bricksmash'] = convolve(run_infos['reward_bricksmash'], np.ones(10), mode='same')
        run_infos['reward_enemykill_stomp'] = np.select([run_infos[f'enemy_kill3{i}']==4 for i in range(0, 6)], [1 for i in range(0, 6)], 0)
        run_infos['reward_enemykill_kick'] = np.select([run_infos[f'enemy_kill3{i}']==132 for i in range(0, 6)], [1 for i in range(0, 6)], 0)
        run_infos['reward_enemykill_impact'] = np.select([run_infos[f'enemy_kill3{i}']==34 for i in range(0, 6)], [1 for i in range(0, 6)], 0)
        run_infos['reward_powerup_taken'] = np.select([run_infos['player_state'] == 9, run_infos['player_state'] == 12, run_infos['player_state'] == 13], [1, 1, 1], 0)

        # loss events
        run_infos['loss_powerup_miss'] = run_infos['powerup_yes_no'] + run_infos['reward_powerup_taken']
        run_infos['loss_powerup_miss'] = run_infos['loss_powerup_miss'].diff().fillna(0)
        run_infos['loss_powerup_miss'] = np.where(run_infos['loss_powerup_miss'] == -46, 1, 0)
        if do_convolve:
            run_infos['loss_powerup_miss'] = convolve(run_infos['loss_powerup_miss'], np.concatenate((np.zeros(30), np.ones(30))), mode='same')
        run_infos['loss_powerdown'] = np.where(run_infos['player_state'] == 10, 1, 0)
        run_infos['loss_dying'] = np.where(run_infos['player_state'] == 11, 1, 0)

        # npcs onscreen
        run_infos['onscreen_enemy'] = np.select([run_infos[f'enemy_drawn1{i}']==1 for i in range(5, 10)], [1 for i in range(5, 10)], 0)
        run_infos['onscreen_powerup'] = np.where(run_infos['powerup_yes_no'] == 46, 1, 0)

        # movement/action events
        run_infos['action_fire'] = np.where(run_infos['fireball_counter'].diff().fillna(0) == 1, 1, 0)
        run_infos['action_leftwalk'] = np.where((run_infos['moving_direction'] == 2) & (run_infos['walk_animation'] == 152), 1, 0)
        run_infos['action_leftrun'] = np.where((run_infos['moving_direction'] == 2) & (run_infos['walk_animation'] == 228), 1, 0)
        run_infos['action_rightwalk'] = np.where((run_infos['moving_direction'] == 1) & (run_infos['walk_animation'] == 152), 1, 0)
        run_infos['action_rightrun'] = np.where((run_infos['moving_direction'] == 1) & (run_infos['walk_animation'] == 228), 1, 0)
        run_infos['action_rest'] = np.where(run_infos['walk_animation'] == 48, 1, 0)
        run_infos['action_jump'] = np.where(run_infos['jump_airborne'] == 1, 1, 0)
        # havent really tested these, would rarely happen
        run_infos['action_climbingup'] = np.where(run_infos['player_state'] == 1, 1, 0)
        run_infos['action_pipedown'] = np.where(run_infos['player_state'] == 3, 1, 0)
        run_infos['action_crouch'] = np.where(run_infos['player_sprite'] == 50, 1, 0)

        # plot desired variables to see how they change with frame-by-frame gameplay
        vars_to_plot = [run_infos['reward_bricksmash'], run_infos['score_increment'], run_infos['jump_airborne']]
        labels = ['reward_bricksmash', 'score_increment', 'jump_airborne']

        plot_explorer(frame_imgs_arrs, vars_to_plot, labels, False)

        # put all useful variables in one df
        run_infos = run_infos[relevant_events]
        run_infos.reset_index(inplace=True, drop=True)
        run_actions.reset_index(inplace=True, drop=True)
        events = pd.concat([run_infos, run_actions], axis=1)
        events = events.loc[:, :].replace(1.0, pd.Series(events.columns, events.columns))
        events = events.replace(0.0, False)
        events = events.loc[:, :].replace(True, pd.Series(events.columns, events.columns))

        durations = pd.DataFrame(columns=list(events.columns))
        collapsed_events = []
        for col in list(events.columns):
            durations[col] = events.groupby(events[col].ne(events[col].shift()).cumsum())[col].transform('size')
            trial_type = list(events[col].loc[events[col].shift() != events[col]])
            duration = list(durations[col].loc[events[col].shift() != events[col]])
            onset = list(events[col].loc[events[col].shift() != events[col]].index)
            df = pd.DataFrame(data=np.array([onset, duration, trial_type]).T, columns=['onset', 'duration', 'trial_type'])
            collapsed_events.append(df)

        event_df = pd.concat(collapsed_events)
        event_df.reset_index(drop=True, inplace=True)
        event_df.drop(index=event_df[event_df['trial_type'] == 'False'].index, inplace=True)
        event_df.drop(index=event_df[event_df['trial_type'] == 0].index, inplace=True)
        event_df['onset'] = event_df['onset'].astype(int)
        event_df['duration'] = event_df['duration'].astype(int)
        event_df.sort_values('onset', inplace=True)
        event_df.reset_index(drop=True, inplace=True)
        event_df['onset'] = event_df['onset'].divide(60)
        event_df['duration'] = event_df['duration'].divide(60)
        event_df = event_df.round(3)


        event_df.to_csv('event_final.csv')

        save_as = f'{task}_{sub}_{run}_events.tsv'

        save_as = check_presence(save_as, out_files)
        save_as = os.path.join(out_dir, save_as)
        event_df.to_csv(save_as, index=False, sep='\t')

    print('Event file created for {}, {}'.format(sub, run))
    return 1


if __name__ == "__main__":
    sub_num, ses_num = take_input()
    data_dir, main, _, out_dir, out_files = setup_io_files(sub_num, ses_num)
    if len(main) == 0:
        print("Can't find data for subject {}".format(sub_num))
        quit()
    else:
        for file in main:
            extract_events(file, data_dir, out_files, out_dir)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, TextBox
import pandas as pd
import retro
import os

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

retro.data.Integrations.add_custom_path("/home/himanshu/Desktop/IBC/cognitive_protocols/mario/data/videogames/mario")
print("SuperMarioBros-Nes" in retro.data.list_games(inttype=retro.data.Integrations.CUSTOM_ONLY))

root = '/home/himanshu/Desktop/IBC/cognitive_protocols/mario/output/sourcedata/sub-98/ses-1/'

names = ['sub-98_ses-1_20230322-152436_SuperMarioBros-Nes_Level1-1_000']


bk2s = [os.path.join(root, i+'.bk2') for i in names]
npzs = [os.path.join(root, i+'.npz') for i in names]

index = 0

if ~os.path.isfile(npzs[index]):
    os.system(f'python play_session.py {bk2s[index]} -i -a')

data = np.load(npzs[index], allow_pickle=True)
for key in data.keys():
    print(key)

# make a dict for data['info']
info = {
    k: [d.get(k) for d in data['info']]
    for k in set().union(*data['info'])
}

info_df = pd.DataFrame(data=info)
emulator, movie, duration = load_movie(bk2s[index])

frame_imgs_arr = create_frames(emulator, movie, video_delay=0)

fig, axs = plt.subplots(1, 2, figsize=(10, 5))
fig.subplots_adjust(bottom=0.25)


im = axs[0].imshow(frame_imgs_arr[0])

# info_df['powerup_appear'].add(1).add(info_df['powerup_yes_no']).multiply(info_df['powerstate'].divide(100000)).plot(ax=axs[1], label="combination")

info_df['powerup_appear'].add(1).multiply(info_df['powerup_yes_no']).plot(ax=axs[1], label="combination")

# info_df['powerup_appear'].plot(ax=axs[1])
# info_df['powerstate'].divide(100000).plot(ax=axs[1], label='powerstate/1e5')
# info_df['powerup_yes_no'].plot(ax=axs[1])

info_df[['player_state']].plot(ax=axs[1])

# info_df['score'].plot(ax=axs[1])
axs[1].set_title('All vars')
axs[1].legend()

# Create the RangeSlider
slider_ax = fig.add_axes([0.20, 0.1, 0.60, 0.03])
slider = Slider(slider_ax, "Frame", 0, len(info_df), valstep=1)

axbox = fig.add_axes([0.81, 0.1, 0.08, 0.04])
text_box = TextBox(axbox, "", initial=0, textalignment="center")

# Create the Vertical lines on the histogram
upper_limit_line = axs[1].axvline(slider.val, color='k')

def update(val):
    # The val passed to a callback by the RangeSlider will
    # be a tuple of (min, max)
    # Update the image's colormap
    t = int(val)

    axs[0].imshow(frame_imgs_arr[t])

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

    axs[0].imshow(frame_imgs_arr[t])

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

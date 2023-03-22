#%%
import numpy as np
import os
import retro
import matplotlib.pyplot as plt
import pandas as pd
# %%

retro.data.Integrations.add_custom_path("/home/himanshu/Desktop/IBC/cognitive_protocols/mario/data/videogames/mario")
print("SuperMarioBros-Nes" in retro.data.list_games(inttype=retro.data.Integrations.CUSTOM_ONLY))
env = retro.make("SuperMarioBros-Nes", inttype=retro.data.Integrations.CUSTOM_ONLY)
print(env)


os.system('python play_session.py /home/himanshu/Desktop/IBC/x-working/new-tasks/courtois_neuromod/task_stimuli/output/sourcedata/sub-test/ses-test/sub-test_ses-test_20230217-161617_SuperMarioBros-Nes_Level1-1_000.bk2 -i -a')

# %%
movie_file = '/home/himanshu/Desktop/IBC/x-working/new-tasks/courtois_neuromod/task_stimuli/output/sourcedata/sub-test/ses-test/sub-test_ses-test_20230217-161617_SuperMarioBros-Nes_Level1-1_000.npz'

data = np.load(movie_file, allow_pickle=True)
for key in data.keys():
    print(key)

data['info']
data['actions']

bar = {
    k: [d.get(k) for d in data['info']]
    for k in set().union(*data['info'])
}

df_info = pd.DataFrame(data=bar)
df_info.plot()
# %%
def load_movie(movie_file):
    movie = retro.Movie(movie_file)
    duration = -1
    while movie.step():
        duration += 1
    movie = retro.Movie(movie_file)
    movie.step()
    emulator = retro.make(game=movie.get_game(), state=retro.State.NONE, use_restricted_actions=retro.Actions.ALL, players=movie.players)
    data = movie.get_state()
    emulator.initial_state = data
    emulator.reset()
    return emulator, movie, duration


emulator, movie, duration = load_movie(movie_file)

emulator.__dict__
plt.imshow(emulator.__dict__['img'])

for i in range(5079):
    keys = data['actions'][i]
    display, reward, done, info = emulator.step(keys)
    print(f'{display}\n{reward}\n{done}\n{info}')
    if True in keys:
        break
    
print(i)
plt.imshow(emulator.__dict__['img'])
# %%
df_info['powerstate'].plot()
df_info['powerup_appear'].plot()
# power up on screen
df_info['powerup_appear'].add(1).add(df_info['powerstate']).multiply(df_info['powerup_yes_no'].mul(0.10)).plot()
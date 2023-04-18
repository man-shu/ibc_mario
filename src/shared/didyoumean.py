import os
from importlib.util import find_spec
from textdistance import jaro


def suggest_session_tasks(query):
    ses_dir_path = find_spec('src.sessions').submodule_search_locations._path[0]
    avail_sess = [s.replace("ses-","").replace(".py","") for s in os.listdir(ses_dir_path)]
    return max(avail_sess, key=lambda x: jaro(x, query))

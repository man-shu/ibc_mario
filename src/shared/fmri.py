from psychopy import core, event, logging, visual
from psychopy.hardware.emulator import launchScan
import time
# from config import WRAP_WIDTH

MR_settings = {
    "TR": 2.000,  # duration (sec) per whole-brain volume
    "sync": ["t", "percent"],  # character to use as the sync timing event; assumed to come at start of a volume
    "skip": 0,  # number of volumes lacking a sync pulse at start of scan (for T1 stabilization)
}

globalClock = core.Clock()


def get_ttl():
    allKeys = event.getKeys(MR_settings["sync"])
    for key in allKeys:
        if key.lower() in MR_settings["sync"]:
            return True
    return False


# blocking function (iterator)
def wait_for_ttl(exp_win, ctl_win):
    get_ttl()  # flush any remaining TTL keys
    ttl_index = 0
    logging.exp(msg="waiting for fMRI TTL")
    red_cross = visual.TextStim(
                    exp_win,
                    text="+",
                    alignText="center",
                    color='red',
                    wrapWidth=2,
                    height=0.2
                )
    while True:
        if get_ttl():
            # TODO: log real timing of TTL?
            logging.exp(msg="fMRI TTL %d" % ttl_index)
            ttl_index += 1
            return
        red_cross.draw(exp_win)
        exp_win.flip()
        if ctl_win:
            red_cross.draw(ctl_win)
            ctl_win.flip()
        time.sleep(0.0005)  # just to avoid looping to fast
        yield

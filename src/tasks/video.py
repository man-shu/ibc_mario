import os, sys, time

#import psychopy
#psychopy.prefs.hardware['audioLib'] = ['PTB', 'sounddevice', 'pyo','pygame'] # for local dev (laptop)
import numpy as np
from psychopy import visual, core, data, logging
from .task_base import Task

from ..shared import config

FADE_TO_GREY_DURATION = 2


class SingleVideo(Task):

    DEFAULT_INSTRUCTION = """You are about to watch a video.
Please keep your eyes open,
and fixate the dot at the beginning and end of the segment."""

    FIXTASK_INSTRUCTION = """Please watch the video normally,
and fixate the dot whenever it appears."""

    def __init__(self, filepath, *args, **kwargs):
        self._aspect_ratio = kwargs.pop("aspect_ratio", None)
        self._scaling = kwargs.pop("scaling", None)
        self._startend_fixduration = kwargs.pop("startend_fixduration", 0)
        self._inmovie_fixations = kwargs.pop("inmovie_fixations", False)
        self._infix_freq = kwargs.pop("infix_freq", 20)
        self._infix_dur = kwargs.pop("infix_dur", 1.5)
        instruct = self.__class__.FIXTASK_INSTRUCTION if self._inmovie_fixations else self.__class__.DEFAULT_INSTRUCTION
        super().__init__(instruction=instruct, **kwargs)
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            raise ValueError(f"File {self.filepath} does not exists")

    def _instructions(self, exp_win, ctl_win):
        screen_text = visual.TextStim(
            exp_win,
            text=self.instruction,
            alignText="center",
            color="white",
            wrapWidth=config.WRAP_WIDTH,
        )

        for frameN in range(config.FRAME_RATE * config.INSTRUCTION_DURATION):
            grey = [
                -float(frameN) / config.FRAME_RATE / config.INSTRUCTION_DURATION
            ] * 3
            exp_win.setColor(grey, colorSpace='rgb')
            screen_text.draw(exp_win)
            if ctl_win:
                ctl_win.setColor(grey)
                screen_text.draw(ctl_win)
            yield True

    def _setup(self, exp_win):

        if self._startend_fixduration > 0 or self._inmovie_fixations:
            from ..shared.eyetracking import fixation_dot
            self.fixation_dot = fixation_dot(exp_win)
            try:
                self.fixation_image = visual.ImageStim(
                    exp_win,
                    os.path.join(
                        "data",
                        "videos",
                        "fixations",
                        f"fixframe_{str(exp_win.size[0])}_{str(exp_win.size[1])}.jpg",
                    ),
                    size=(exp_win.size[0], exp_win.size[1]),
                    units='pix',
                )
            except:
                self.fixation_image = visual.ImageStim(
                                        exp_win,
                                        os.path.join("data", "videos", "fixations", "fixframe.jpg"),
                                        size=(exp_win.size[1]*(1280/1024), exp_win.size[1]),
                                        #size=(1280, 1024),
                                        units='pix',
                )
                #print(exp_win.size)

        if self._inmovie_fixations:
            self.grey_bgd = visual.Rect(exp_win, size=exp_win.size, lineWidth=0,
                                        colorSpace='rgb', fillColor=(-.58, -.58, -.58)) # (54, 54, 54) on 0-255 scale
            self.black_bgd = visual.Rect(exp_win, size=exp_win.size, lineWidth=0,
                                        colorSpace='rgb', fillColor=(-1, -1, -1))
            self.startcue = visual.Circle(exp_win, units='pix', pos=(0,0), radius=10, lineWidth=0, fillColor=(1, 1, 1))
            self.markers = np.asarray(
                [
                    (0.5, 0.5),
                    (0, 0.5),
                    (0.0, 1.0),
                    (0.5, 1.0),
                    (1.0, 1.0),
                    (1.0, 0.5),
                    (1.0, 0.0),
                    (0.5, 0.0),
                    (0.0, 0.0),
                ]
            )
            self.markers_order = np.random.permutation(np.arange(len(self.markers)))
            self.marker_duration = 1.5 # 60 fps, 4s = 240; 60fps, 1.5s = 90 frames

        #self.movie_stim = visual.MovieStim3(exp_win, self.filepath, units="pix")
        self.movie_stim = visual.MovieStim2(exp_win, self.filepath, units="pix")

        # print(self.movie_stim._audioStream.__class__)
        aspect_ratio = (
            self._aspect_ratio or self.movie_stim.size[0] / self.movie_stim.size[1]
        )
        min_ratio = min(
            exp_win.size[0] / self.movie_stim.size[0],
            exp_win.size[1] / self.movie_stim.size[0] * aspect_ratio,
        )

        width = min_ratio * self.movie_stim.size[0]
        height = min_ratio * self.movie_stim.size[0] / aspect_ratio

        if self._scaling is not None:
            width *= self._scaling
            height *= self._scaling

        self.movie_stim.size = (width, height)
        self.duration = self.movie_stim.duration
        #        print(self.movie_stim.size)
        #        print(self.movie_stim.duration)
        super()._setup(exp_win)

    def _run(self, exp_win, ctl_win):
        # give the original size of the movie in pixels:
        # print(self.movie_stim.format.width, self.movie_stim.format.height)
        exp_win.logOnFlip(
            level=logging.EXP, msg="video: task starting at %f" % time.time()
        )
        mv_FPS = self.movie_stim.getFPS()
        fixation_on = False  # "switch" to determine fixation onset/offset time for logs
        self.movie_stim.play()

        while self.movie_stim.status != visual.FINISHED:
        #while self.movie_stim.getCurrentFrameNumber() < 200:
            #exp_win.clearBuffer(color=True, depth=True)

            self.movie_stim.draw(exp_win)
            next_frame_time = self.movie_stim.getCurrentFrameTime()
            # MovieStim3: https://github.com/psychopy/versions/blob/3327a7215c08e8390237f2e6c08259735ef093aa/psychopy/visual/movie3.py#L346
            #next_frame_num = int(next_frame_time * mv_FPS)
            # MovieStim2: https://github.com/psychopy/psychopy/blob/b77e73a78e41365cb999fac2f288bc659377ccf6/psychopy/visual/movie2.py#L581
            next_frame_num = self.movie_stim.getCurrentFrameNumber()

            if ctl_win:
                self.movie_stim.draw(ctl_win)
            '''
            Added: option to either have fixations @ start/end of run,
            or to have them at regular intervals through the run (w logged time)
            For within-run fixations, endstart_fixduration must be set to 0.0 (from ses-friends-s6.py file)
            '''
            if self._startend_fixduration > 0:
                if next_frame_time <= self._startend_fixduration or \
                        next_frame_time >= self.movie_stim.duration-self._startend_fixduration:
                    self.fixation_image.draw(exp_win)
                    #exp_win.clearBuffer(color=True, depth=True)
                    #for stim in self.fixation_dot:
                    #    stim.draw(exp_win)
                    fixation_on = True
            elif self._inmovie_fixations:
                if (next_frame_time % self._infix_freq < self._infix_dur):
                    '''
                    Of note, the grey_bgd color matches the mean intensity of Friends frames, but adding black full-screen frame
                    after fixation offset introduces weird flickering. Black fixation background good enough?
                    #self.grey_bgd.draw(exp_win)
                    Update: clearing the buffer before the next flip removes the movie frame without
                    having to layer a grey or black background under the fixation target.
                    '''
                    self.fixation_image.draw(exp_win)
                    #exp_win.clearBuffer(color=True, depth=True)
                    #for stim in self.fixation_dot:
                    #    stim.draw(exp_win)
                    if not fixation_on:
                        exp_win.logOnFlip(
                            level=logging.EXP, msg="fixation onset at frame %d at %f" % (next_frame_num, time.time()) # log fix onset time
                        )
                        self._events.append({
                            'event_type': 'fixation',
                            'onset_frame': next_frame_num,
                            'onset_time': next_frame_time,
                        })
                        fixation_on = True
                elif fixation_on:
                    exp_win.logOnFlip(
                        level=logging.EXP, msg="fixation offset at frame %d at %f" % (next_frame_num, time.time()) # log fix offset time
                    )
                    self._events[-1].update({
                        'offset_frame': next_frame_num,
                        'offset_time': next_frame_time,
                    })
                    fixation_on = False

            if not self._inmovie_fixations and next_frame_num % 100 == 0:
                exp_win.logOnFlip(
                    level=logging.EXP, msg="Frame %d at %f" % (next_frame_num, time.time()) # log frame time every 100 frames
                )

            yield False

        self.movie_stim.pause()

        if self._inmovie_fixations:
            window_size_frame = exp_win.size - 100 * 2
            instruction_text = """Eyetracker Validation"""
            screen_text = visual.TextStim(
                exp_win,
                text=instruction_text,
                alignText="center",
                color="white",
                wrapWidth=config.WRAP_WIDTH,
            )
            for _ in range(config.FRAME_RATE * 2):
                screen_text.draw(exp_win)
                if ctl_win:
                    screen_text.draw(ctl_win)
                yield True

            exp_win.logOnFlip(
                level=logging.EXP, msg=" gaze validation: starting at %f" % time.time())

            for _ in range(config.FRAME_RATE * 1):
                self.startcue.draw(exp_win)
                if ctl_win:
                    self.startcue.draw(ctl_win)
                yield True

            for site_id in self.markers_order:
                marker_pos = self.markers[site_id]
                pos = (marker_pos - 0.5) * window_size_frame # remove 0.5 since 0, 0 is the middle in psychopy

                for stim in self.fixation_dot:
                    stim.pos = pos

                exp_win.logOnFlip(
                    level=logging.EXP,
                    msg="marker position,%f,%f,%d,%d starting at %f"
                    % (marker_pos[0], marker_pos[1], pos[0], pos[1], time.time()))

                for _ in range(int(config.FRAME_RATE * self.marker_duration)):
                    for stim in self.fixation_dot:
                        stim.draw(exp_win)
                        if ctl_win:
                            stim.draw(ctl_win)
                    yield True

                exp_win.logOnFlip(
                    level=logging.EXP,
                    msg="marker position,%f,%f,%d,%d ending at %f"
                    % (marker_pos[0], marker_pos[1], pos[0], pos[1], time.time()))


    def _stop(self, exp_win, ctl_win):
        self.movie_stim.stop()

        for frameN in range(config.FRAME_RATE * FADE_TO_GREY_DURATION):
            grey = [float(frameN) / config.FRAME_RATE / FADE_TO_GREY_DURATION - 1] * 3
            exp_win.setColor(grey, colorSpace='rgb')
            if ctl_win:
                ctl_win.setColor(grey)
            yield True

    def _restart(self):
        self.movie_stim.setMovie(self.filepath)

    def unload(self):
        del self.movie_stim


class VideoAudioCheckLoop(SingleVideo):

    DEFAULT_INSTRUCTION = """We are setting up for the MRI session.
Make yourself comfortable.
We will play your personalized video so that you can ensure you can see the full screen and that the image is sharp."""

    def _setup(self, exp_win):
        super()._setup(exp_win)
        # set infinite loop for setup, need to be skipped
        self.movie_stim.loop = -1
        self.use_fmri = False
        self.use_eyetracking = False

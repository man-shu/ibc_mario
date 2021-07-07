import time
import textwrap
import os
import pandas
from psychopy import visual, data, core, event
from .task_base import Task
from ..shared import config, utils

def displayText(windows, textContent):
    wrapWidth = config.WRAP_WIDTH

    # Deindent text content.
    textContent = textwrap.dedent(textContent)

    # For every window.
    for window in windows:
        # Ignore None.
        if window is None:
            continue
        
        # Setup text.
        # @warning used to be setup only for exp_win, then displayed on both.
        screen_obj = visual.TextStim(
            window,
            text=textContent,
            alignText="center",
            color="white",
            wrapWidth=wrapWidth,
        )

        # Display text on window.
        screen_obj.draw(window)

        # @note will be done through yield.
        window.flip(clearBuffer=True)

# @warning backbuffer isn't flipped, image wont be displayed until it is.
def drawImage(windows, image):
    # For every window.
    for window in windows:
        # Ignore None.
        if window is None:
            continue
        
        # Draw image.
        image.draw(window)

def flipBackBuffer(windows):
    # For every window.
    for window in windows:
        # Ignore None.
        if window is None:
            continue
        
        # Display backbuffer and clear it.
        window.flip(clearBuffer=True)

def clearScreen(windows):
    # Clear screen
    # For every window.
    for window in windows:
        # Ignore None.
        if window is None:
            continue
        
        # Clear screen.
        window.flip(clearBuffer=True)

# Like utils.wait_until, but giving back control to the main loop event.
# @params float deadline in seconds
def waitUntil(clock, deadline):
    hogCPUperiod = 0.1
    keyboard_accuracy = .0005

    sleep_until = deadline - hogCPUperiod
    utils.poll_windows()
    current_time = clock.getTime()
    while current_time < deadline:
        # Sleep for a very short while.
        if current_time < sleep_until:
            time.sleep(keyboard_accuracy)

        # Not so sure ? Dispatch event ? Seems not relevant in our case (cf.
        # not sure pyglet is used internally).
        utils.poll_windows()

        # Update time.
        current_time = clock.getTime()

        # Give back control to main event loop.
        yield

def waitFor(duration):
    clock = core.Clock()
    yield from waitUntil(clock, duration)

# otherwise involve the root task to override Task's base methods instead of
# overriding the `protected` (underscored) method, which are meant to be. In
# other word Task is not meant to be used in a hierarchical fashion, even
# though it is possible.
class PrismeDisplayTask():
    _fixationCross = None
    _imageDir = None
    _runImageSetup = None
    _preloadedImages = {}

    def __init__(self, imageDir, runImageSetup):
        self._imageDir = imageDir
        self._runImageSetup = runImageSetup

    # Prefetch large files early on for accurate start with other recordings
    # (scanner, biopac...).
    def prefetch(self, exp_win):
        # Load fixation cross.
        fixationCrossPath = os.path.join('data', 'prisme', 'pngs',
            'fixation_cross.png')
        self._fixationCross = visual.ImageStim(exp_win, fixationCrossPath,
            size=0.5, units='deg')
        
        # Preload images.
        for currImageObj in self._runImageSetup:
            shallowImagePath = currImageObj['image_path']
            fullImagePath = os.path.join(self._imageDir, shallowImagePath)
            # @note path already has been checked within caller.
            self._preloadedImages[shallowImagePath] = visual.ImageStim(
                exp_win, fullImagePath, size=10, units='deg')

    # Run task.
    # @warning must be indempotent due to root task's #restart implementation.
    def run(self, exp_win, ctl_win):
        # Start clock.
        clock = core.Clock()

        # For each images
        for currImageObj in self._runImageSetup:
            # Draw image.
            shallowImagePath = currImageObj['image_path']
            image = self._preloadedImages[shallowImagePath]
            drawImage([exp_win, ctl_win], image)

            # Wait until onset!
            # @warning @todo check why -1 in onset ? (I have since removed it)
            yield from waitUntil(clock, currImageObj['onset'])

            # Display drawn images and clear backbuffer.
            flipBackBuffer([exp_win, ctl_win])

            # Wait for duration.
            yield from waitFor(currImageObj['duration'])

            # Display fixation cross only and clear backbuffer.
            drawImage([exp_win, ctl_win], self._fixationCross)
            flipBackBuffer([exp_win, ctl_win])

            # Give back control to main loop for event handling (optional).
            yield


        # Clear screen.
        clearScreen([exp_win, ctl_win])

        # Give back control to main loop for event handling (optional).
        yield

    def save(self):
        pass

    def teardown(self):
        pass


class PrismeMemoryTask():
    _imageDir = None
    _runImageSetup = None
    _preloadedImages = {}
    _events = pandas.DataFrame()
    _trial = None

    def __init__(self, imageDir, runImageSetup):
        self._imageDir = imageDir
        self._runImageSetup = runImageSetup

        # Generate trial, used to store events.
        self._trial = data.TrialHandler(self._runImageSetup, 1, method="sequential")

    # Prefetch large files early on for accurate start with other recordings
    # (scanner, biopac...).
    def prefetch(self, exp_win):
        # Preload images.
        for currImageObj in self._runImageSetup:
            shallowImagePath = currImageObj['image_path']
            fullImagePath = os.path.join(self._imageDir, shallowImagePath)
            # @note path already has been checked within caller.
            self._preloadedImages[shallowImagePath] = visual.ImageStim(
                exp_win, fullImagePath, size=10, units='deg')

    # Display instructions (without any pause, in order to control for memory
    # effect induced by delay).
    def instructions(self, exp_win, ctl_win):
        duration = config.INSTRUCTION_DURATION

        # Start clock.
        clock = core.Clock()

        # Display text.
        displayText([exp_win, ctl_win], """\
            Appuyez sur le bouton correspondant à chaque image
            étant apparu lors de la séquence précédente.
            VU (bouton gauche)    NON VU (bouton droit)
        """)
        
        # Wait for the time of the instruction.
        yield from waitUntil(clock, duration)
        
        # Clear screen.
        clearScreen([exp_win, ctl_win])

        # Give back control to main loop for event handling (optional).
        yield

    # Run task.
    # @warning must be indempotent due to root task's #restart implementation.
    def run(self, exp_win, ctl_win):
        RESPONSE_KEYS = ['a','b','c','d']
        
        # Start clock.
        clock = core.Clock()

        # Clear events.
        event.clearEvents()

        # For each images
        for trial in self._trial:
            currImageObj = trial

            # Draw image.
            shallowImagePath = currImageObj['image_path']
            image = self._preloadedImages[shallowImagePath]
            drawImage([exp_win, ctl_win], image)

            # Wait until onset!
            # @warning @todo check why -1 in onset ? (I have since removed it).
            yield from waitUntil(clock, currImageObj['onset'])

            # Display drawn images and clear backbuffer.
            flipBackBuffer([exp_win, ctl_win])
            
            # Wait for duration.
            yield from waitFor(currImageObj['duration'])

            # Retrieve events.
            keypresses = event.getKeys(RESPONSE_KEYS, timeStamped=clock)
            trial['keypresses'] = keypresses

            # Give back control to main loop for event handling (optional).
            yield

        # Clear screen.
        clearScreen([exp_win, ctl_win])

        # Give back control to main loop for event handling (optional).
        yield

    def restart(self):
        # Generate trial, used to store events.
        self._trial = data.TrialHandler(self._runImageSetup, 1, method="sequential")

    def save(self, outputTsvPath):
        self._trial.saveAsWideText(outputTsvPath)
        pass

    def teardown(self):
        pass

# @note the main loop is designed to run a single task every run, more task
# will lead to multiple fmri TTL awaiting in case of --fmri flag.
class PrismeTask(Task):
    # - Setup
    _displayTask = None
    _memoryTask = None
    _doRestart = False
    _imageDir = None
    _runImageSetup = None
    
    # Class constructor.
    def __init__(self, patientImageSetupPath, imageDir,
                 runIdx, *args, **kwargs):
        super().__init__(**kwargs)

        # Import run's image list.
        print('runIdx', runIdx)
        print('patientImageSetupPath: %s' % patientImageSetupPath)
        patientImageSetup = data.importConditions(patientImageSetupPath)
        runImageSetup = [
            currImageObj for currImageObj in patientImageSetup
            if currImageObj['run'] == runIdx and currImageObj['type'] == 'fmri'
        ]
        
        # Ensure image exists.
        for currImageObj in runImageSetup:
            fullImagePath = os.path.join(imageDir, currImageObj['image_path'])
            if not os.path.exists(imageDir) or not \
               os.path.exists(fullImagePath):
                raise ValueError('Cannot find the listed image %s ' %
                                 fullImagePath)
        
        # Store setup.
        self._imageDir = imageDir
        self._runImageSetup = runImageSetup
        
        # Instantiate sub-tasks.
        self._displayTask = PrismeDisplayTask(self._imageDir, [
            currImageObj for currImageObj in self._runImageSetup
            if currImageObj['condition'] == 'shown'
        ])
        self._memoryTask = PrismeMemoryTask(self._imageDir, [
            currImageObj for currImageObj in self._runImageSetup
            if currImageObj['condition'] in ['neg', 'pos']
        ])

    # Prefetch large files early on for accurate start with other recordings
    # (scanner, biopac...).
    def _setup(self, exp_win):
        self._displayTask.prefetch(exp_win)
        self._memoryTask.prefetch(exp_win)

    # - Task loops

    # @note
    # The core of the software architecture is designed as a general main loop,
    # processing task and events bits by bits.
    # Any yield within the underlying sub-loops gives back software's control
    # to the main loop, thus letting inputs (such as. <ctrl>-C) be processed.
    # Once the main loop has finished its temporary job, it gives back control
    # to the python method (generator). It also record a movie frame every 6th
    # yield if --record-movie is enabled.

    # 1st task loop
    # `Awaiting` task loop, to be displayed while awaiting fmri TTL to be sent
    # (in case flag --fmri is on), before eyetracker has started recording,
    # before EEG TTL has been sent, etc etc.
    #
    # @warning
    # Other instructions such as eyetracking may already have been displayed.
    # @warning
    # Main loop seems not to contain any sleep to wait inbetween frame so
    # it's likely all frames will be run at once, and event will be
    # ignored until next frame is yield.
    # @note main loop doesn't rely on generator argument, but Task
    # (base_task) use it in order to know if it has to clear the buffer
    # after (when True) displaying the frame (by flipping the backbuffer), but
    # only when using #_instructions instead of #instructions.
    def instructions(self, exp_win, ctl_win):
        duration = config.INSTRUCTION_DURATION

        # Start clock.
        clock = core.Clock()

        # Display text.
        displayText([exp_win, ctl_win], """\
            Veuillez regardez les images durant les 5 prochaines minutes
            en essayant de ne pas bouger la tête.
        """)
        
        # Wait for the time of the instruction.
        yield from waitUntil(clock, duration)
        
        # Clear screen.
        clearScreen([exp_win, ctl_win])

        # Give back control to main loop for event handling (optional).
        yield

    # @note main loop will wait for TTL here if --fmri flag is enabled.
    # @note eeg spike will be sent here if --eeg flag is enabled.
    # @note eyetracking record will start here if --eyetracking flag is enabled.

    # 2nd task loop
    # `Running` task loop, to be displayed while everything is recording (eeg,
    # eyetracker, fmri, etc).
    # @warning
    # self._doRestart within loops might be checked with a slight delay.
    def run(self, exp_win, ctl_win):
        # First run the display task, yielding back control to the main loop
        # for a bit at every step.
        displayTaskLoop = self._displayTask.run(exp_win, ctl_win)
        for idx, _ in enumerate(displayTaskLoop):
            if self._doRestart:
                break
            else:
                yield _

        # Restart the Task/Run if requested by main loop.
        if self._doRestart:
            self._doRestart = False
            return self._run(exp_win, ctl_win)

        # Then display memory task instruction and start it without a pause to
        # control for a stable delay in order to avoid the difference in delay
        # to impact person's memory and thus final result.
        memoryInstructionLoop = self._memoryTask.instructions(exp_win, ctl_win)
        for idx, _ in enumerate(memoryInstructionLoop):
            if self._doRestart:
                break
            else:
                yield _
        
        # Restart the Task/Run if requested by main loop.
        if self._doRestart:
            self._doRestart = False
            return self._run(exp_win, ctl_win)
    
        # Then run the memory task, yielding back control to the main loop
        # for a bit at every step.
        memoryTaskLoop = self._memoryTask.run(exp_win, ctl_win)
        for idx, _ in enumerate(memoryTaskLoop):
            if self._doRestart:
                break
            else:
                yield _

        # Restart the Task/Run if requested by main loop.
        if self._doRestart:
            self._doRestart = False
            return self._run(exp_win, ctl_win)

    # @note eeg spike will be sent here if --eeg flag is enabled.

    # 3rd task loop
    # `Ending` task loop, to be displayed after everything has been recorded
    # (but before events are stored, which is when the #_save method is called).
    def _stop(self, exp_win, ctl_win):
        yield

    # - Tear down

    # Override events saving if transformation are needed.
    # @returns False if events need not be saved
    def _save(self):
        eventsTsvPath = self._generate_unique_filename('events', 'tsv')
        self._displayTask.save()
        self._memoryTask.save(eventsTsvPath)
        return False  # we save events ourselves, without relying on the
                      # underlying framework.

    # Restart the current task, when <ctrl>-n is hit (the main loop take care
    # of listening to the event and then call this method, but doesn't do
    # anything else, such as reinstantiating the class).
    def _restart(self):
        self._doRestart = True

        # Regenerate trial, used to store events.
        self._memoryTask.restart()

    # Called after everything from the task has run (including #_save).
    def unload(self):
        self._displayTask.teardown()
        self._memoryTask.teardown()

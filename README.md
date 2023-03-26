## Display settings

* Extend the primary display to the slave monitor.
* Display resolution - 1920 x 1080, refresh rate - 60 Hz.

## Other Setup

* Connect the teensy board's USB cable to the laptop
* All keys should report OK
* If not, try disconnecting the respective optic fiber, and reconnecting and/or polishing the terminals
* Reconnect the USB and make sure all keys report OK
* Just to be sure, ask the subject to press the keys too

## How to run

* Make sure the conda environment is active
	
	```
	conda activate py38psypy
	```

* Go into the task folder:
	
	```
	cd C:\Users\Public\gitrepos\cognitive_protocols\mario
	```

## Practice

* No practice, just make sure that the subject has read the instructions

## Scanner task

* Run the script `main.py` as follows:
	
	```
	python main.py --subject {test} --session {test} --tasks mario-ibc -o output/ --fmri
	```

* Enter subject and session numbers inplace of `{test}`.
* There are six runs. In case of a restart, delete the files corresponsding to the faulty run in the `output/sourcedata` directory

## How to quit

Press `Ctrl+C` anytime.

## Responses

* 8 buttons on the gaming controller.

## After the acquisition

`output/sourcedata` folder contains log of the run.  

### Data extraction

* Activate conda environment py38psypy 
	
	```
    conda activate py38psypy
	```

* Run `paradigm_descriptors.py` as follows:

	```
    python paradigm_descriptors.py
	```

* Enter subject number when prompted.

* Output event files would be stored in `output_paradigm_descriptors` folder

## Design

* 6 runs (starting from 1)
* Each run is 10 min 

## Software info

* Python 3.8.5, Psychopy 2021.1.3, Gym retro
* Primary script `main.py`

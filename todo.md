# TODO

* make Mario roms independent of datalad / git, not pushing on repo for now
    - `cd /home/himanshu/Desktop/IBC/x-working/new-tasks/courtois_neuromod/task_stimuli/data/videogames`
    - did `git-annex unannex .`
    - copied the un-linked rom files in `SuperMarioBros-Nes` dir

* might need to install following in addition to requirements:
    * install `dotenv`: pip install python-dotenv
    * install `attrdict`
    * install `wxPython` and prereqs for it
    * install `textdistance`
    * install `gym-retro`: pip install gym==0.25.2 because no hash-seed module in newer version
    * install `datalad`

* run with `python main.py --subject test --session test --tasks mario -o output/`

* one run ends when:
    - level is successfully finished
    - duration is over
    - 3/3 lives have been used 
* make run duration consistent

* screen flickers, by design (?)
* ~~can't move on the survey page with controller~~ 
* interpret logs
    - frame-by-frame key presses
    - score
    - xscrollLo: varies bw 0-255, specifies camera scroll in x direction
    - xscrollHi: varied bw 0-12, don't know what is it
* can add more variables: https://datacrystal.romhacking.net/wiki/Super_Mario_Bros.:RAM_map
    - define them in [data.json](https://github.com/courtois-neuromod/mario.stimuli/blob/main/SuperMarioBros-Nes/data.json)
    ```
    Also to use such modified retro integration, you need to add it to the custom paths retro.data.Integrations.add_custom_path() and then call retro.make with inttype=retro.data.Integrations.CUSTOM_ONLY to override the default Integration.
    ```
    - as mentioned [here](https://retro.readthedocs.io/en/latest/integration.html#using-a-custom-integration-from-python)

     
* ~~recreate sessions with .bk2 files~~
* does controller need `antimicrox`
    - does it add to the lag

* five kinds of events:
    - (rest)
    - action
        - movement (down, left, right, jump, run) (`keypress`)
        - shoot (`keypress`)
    - reward
        - coin (`coins` increment by ?)
        - brick smash (`score` increment ?)
        - enemy kill (increment in `enemy_kill30-35` by `4` if stomped, by `34` if by fire or others)
        - power taken (increment in `(powerup_appear + 1) * powerup_yes_no` by ? and `score` increment by `100`) (duration could be figured out by `player_state`)
    - punishment
        - power down (`powerstate` goes down, maybe better with `player_state`)
        - dying (`player_state`)
    - npc_appear
        - mushroom, flower, star, 1up (increment in `(powerup_appear + 1) * powerup_yes_no` by ?)
        - enemy (`enemy_drawn15-19` keeps track of max 5 enemies on screen, increment by 1 for each)

* relevant RAM states:
    ```
    To check when mario has been hit and reverts to its normal form (if so they lose their current power) you could probably use the invincibility timer :
    0x079E	Timer: invincible after enemy collision. Freeze this register to anything but 0 and you remain invincible
    Alternatively, you can check Mario's state with :
    0x0756	Powerup state
    Finally, detecting when an enemy is killed seems tricky, I didn't try much yet, but I would start with these variables :
    0x001E,0x0023	Enemy state? Haven't tested much.
    0x00 - Does _not_ mean they don't exist
    0x01 - falling_enemy or Bullet_Bill drawn(not killed yet).
    0x04 - Enemy Stomped
    0x20 - BulletBill / CheepCheep / hammer_bro stomped
    0x22 - killed with fire or star
    0x23 - bowser_killed
    0xC4 - koopa stomped falling
    0x84 - koopa or buzzyBeetle Stomped and moving;
    0xFF - Will kill them off (like getting hit by a star)
    ```
    ```
    - 0x0039    Powerup type (when on screen) ("powerup_appear": {"address": 57, "type": "<u1"})
                0 - Mushroom
                1 - Flower
                2 - Star
                3 - 1up
    ```
    ```
    - 0x0756    Powerup state ("powerstate": {"address": 1878, "type": "|u1"})
                0 - Small
                1 - Big
                >2 - fiery
    ```
    ```
    0x001B	Powerup on screen ("powerup_yes_no": {"address": 27, "type": "<u1"})
            0x00 - No
            0x2E - Yes
    ```
    ```
    - 0x0016/A	Enemy type (5x). ("enemy_type": {"address": 22, "type": "|u1"})
                0x00 - Green Koopa
                0x01 - Red Koopa
                0x02 - Buzzy beetle
                0x03 - Red Koopa
                0x04 - Green Koopa
                0x05 - Hammer brother
                0x06 - Goomba
                0x07 - Blooper
                0x08 - BulletBill FrenzyVar
                0x09 - Green Koopa paratroopa
                0x0A - Grey CheepCheep
                0x0B - Red CheepCheep
                0x0C - Pobodoo
                0x0D - Piranha Plant
                0x0E - Green Paratroopa Jump
                0x0F - Crashes game(status bar margin)
                0x10 - Bowser's flame
                0x11 - Lakitu
                0x12 - Spiny Egg
                0x13 - Nothing
                0x14 - Fly CheepCheep
                0x15 - Bowser's Flame
                0x16 - Fireworks
                0x17 - BulletBill Frenzy
                0x18 - Stop Frenzy
                0x1B/0x1C/0x1D/0x1E - Firebar
                0x1F - Long Firebar (castle) AND sets previous enemy slot to 0x20 or else only half of the line shows
                0x24/0x25 - Static lift
                0x26/0x27 - Vertical going lift
                0x28 - Horizontal going lift
                0x29 - Static lift (Will Fall if Player stays on it for too long)
                0x2A - Horizontal forward moving lift with strange hitbox
                0x2B/0x2C - Halves of double lift (like 1.2)
                0x2D - Bowser (special), will try to set previous addr to 2D as well, if unable only his ass shows :) He also tries to reach a certain height, if not there already, before starting his routine.
                0x2E - PowerUp Object
                0x2F - Vine Object
                0x30 - Flagpole Flag Object
                0x31 - StarFlag Object
                0x32 - Jump spring Object
                0x33 - BulletBill CannonVar
                0x34 - Warpzone
                0x35 - Retainer Object
                0x36 - Crash
                0x37 - 2 Little Goomba.
                0x38 - 3 Little Goomba.
                0x3A - Skewed goomba.
                0x3B - 2 Koopa Troopa.
                0x3C - 3 Koopa Troopa.
    only seems to record the brown ones
    ```
    ```
    0x001E,0x0023   Enemy state? Haven't tested much.("enemy_kill": {"address": 35, "type": "|u1"})
                    0x00 - Does _not_ mean they don't exist
                    0x01 - falling_enemy or Bullet_Bill drawn(not killed yet).
                    0x04 - Enemy Stomped
                    0x20 - BulletBill / CheepCheep / hammer_bro stomped
                    0x22 - killed with fire or star
                    0x23 - bowser_killed
                    0xC4 - koopa stomped falling
                    0x84 - koopa or buzzyBeetle Stomped and moving;
                    0xFF - Will kill them off (like getting hit by a star)
    not really kill, maybe level of brown ones
    ```
    ```
    0x0491	Enemy Collision_Bits, Value is set to 0x01 whenever player gets collided with enemy otherwise it stays 0x00.
    "enemy_collision": {
      "address": 1169,
      "type": "|u1"
    }
    ```
    ```
    0x000F-0x0013	Enemy drawn? Max 5 enemies at once.
                    0 - No
                    1 - Yes (not so much drawn as "active" or something)
    "enemy_drawn": {
      "address": 15,
      "type": "|u1"
    }
    ```
    ```
    0x000E	Player's state
            0x00 - Leftmost of screen
            0x01 - Climbing vine
            0x02 - Entering reversed-L pipe
            0x03 - Going down a pipe
            0x04 - Autowalk
            0x05 - Autowalk
            0x06 - Player dies
            0x07 - Entering area
            0x08 - Normal
            0x09 - Transforming from Small to Large (cannot move)
            0x0A - Transforming from Large to Small (cannot move)
            0x0B - Dying
            0x0C - Transforming to Fire Mario (cannot move)
    "player_state": {
      "address": 14,
      "type": "|u1"
    }
    ```
    ```
    0x00D79	Brick smash 1 x
    "brick_smash": {
      "address": 3449,
      "type": "|u1"
    }
    ```
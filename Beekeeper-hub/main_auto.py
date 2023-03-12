# main.py -- put your code here!
# import hub
from serialtalk import SerialTalk
from mshub import MSHubSerial
from pybricks import Direction, Port, ForceSensor, DriveBase, Motor, wait, Stop

# hub.sound.beep()

st = SerialTalk(MSHubSerial('F'))
switch = ForceSensor(Port.E)
print(st)
# Hello there
pass
# Init drivebase
r_track = Motor(Port.A)
l_track = Motor(Port.C, Direction.COUNTERCLOCKWISE)
tracks = DriveBase(l_track, r_track, 50, 125)

# Init drill
drill = Motor(Port.B, Direction.COUNTERCLOCKWISE)

# Init tanks
tanks = Motor(Port.D) 
tanks.run_until_stalled(-200, duty_limit=30) # Run until empty
tanks.reset_angle(0)
TANK_FULL = 155

def set_tank_level(pct):
    pct = min(max(pct,0),100)
    tanks.run_target(50, pct/100 * TANK_FULL, wait=False)

def drill_up():
    drill.run_target(200,5,Stop.BRAKE)

def drill_down():
    drill.run_target(200,80,Stop.BRAKE)

def wriggle(n=3, angle=25):
    tracks.curve(0, -angle/2)
    for i in range(n):
        tracks.curve(0, angle)
        tracks.curve(0, -angle)
    tracks.curve(0, angle/2)
    
def wait_until(function, condition=True):
    while not function() == condition:
        wait(10)

while True:
    if switch.pressed():
        drill_up()
        set_tank_level(100)
        wait_until(switch.pressed, False)
    else:
        wait(1000)
        tracks.straight(100)
        tracks.curve(0, 90)
        drill_down()
        set_tank_level(0)
        wriggle()
        drill_up()
        tracks.straight(-100)
        wait_until(switch.pressed, True)



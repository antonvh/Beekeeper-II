import hub
from serialtalk import SerialTalk
from mshub import MSHubSerial
from pybricks import Direction, Port, ForceSensor, DriveBase, Motor, wait, Stop

hub.sound.play('sounds/startup')

# Open comms
st = SerialTalk(MSHubSerial('F'))

# Define motors and sensors
wait(600) # Some time to handshake hub object and motors
switch = ForceSensor(Port.E)

# Init drivebase
r_track = Motor(Port.A)
l_track = Motor(Port.C, Direction.COUNTERCLOCKWISE)
tracks = DriveBase(l_track, r_track, 41.5, 160)

# Init drill
drill = Motor(Port.B, Direction.COUNTERCLOCKWISE)

# Init tanks
tanks = Motor(Port.D) 
tanks.run_until_stalled(-200, duty_limit=45) # Run until empty
tanks.reset_angle(-10) # Add some extra -10 degrees to make sure 0 is without motor tension
TANK_FULL = 160 # Degrees motor position.

def set_tank_level(pct):
    pct = min(max(pct,0),100) # Cap percentage
    tanks.run_target(50, pct/100 * TANK_FULL, wait=False)
set_tank_level(100)

def get_tank_level():
    # Return a number between 0 and 100, relative to the 
    # tank motor angle/tank fill level.
    return min(max( tanks.angle()*100//TANK_FULL, 0), 100)

def resting():
    return 1 if switch.pressed() else 0

def status():
    return {
        'rst': resting(),
        'bat': hub.battery.capacity_left(),
        'chg': 1 if hub.battery.charger_detect() else 0,
        'tnk': get_tank_level(),
        }

def not_when_resting(func):
    # Decorator to ensure the robot does not move when in its cradle
    def cradle_safe_func(*args, **kwargs):
        if not resting():
            func(*args, **kwargs)
        return status()
    return cradle_safe_func

@not_when_resting    
def drill_up():
    drill.run_target(200,5,Stop.BRAKE)

@not_when_resting
def drill_down():
    drill.run_target(200,80,Stop.BRAKE)

@not_when_resting
def wriggle(n=3, angle=25):
    tracks.curve(0, -angle/2)
    for i in range(n):
        tracks.curve(0, angle)
        tracks.curve(0, -angle)
    tracks.curve(0, angle/2)
        
def sound_loaded():
    hub.sound.play('sounds/menu_program_start')

@not_when_resting
def straight(distance=100):
    tracks.straight(distance)

@not_when_resting
def turn(radius=0, angle=90):
    tracks.curve(radius, angle)


st.add_command(get_tank_level,"b")
st.add_command(set_tank_level, "repr")
# Can't get name of closures resulting from decorators
# So adding them explicitly with name=
st.add_command(wriggle, "repr", name="wriggle")  
st.add_command(drill_down, "repr", name="drill_down")
st.add_command(drill_up, "repr", name="drill_up")
st.add_command(straight, "repr", name="straight")
st.add_command(turn, "repr", name="turn")
st.add_command(hub.sound.beep, "repr", name="beep")
st.add_command(sound_loaded, "repr")
st.add_command(status, "repr")
st.loop()



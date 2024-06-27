import time
import struct
import subprocess

class VASTController:
    
    # 1 um = 21333.33 microsteps
    # 1 step = 0.72 degrees
    UM_TO_US = 21.33333
    DEG_TO_US = 1 / 0.72

    def __init__(self):
        self.holster = "C:\\Users\\mesoO\\Documents\\TestAutoSampIntegration\\bin\\Debug\\TestAutoSampIntegration.exe"
        self.f = None
        self.vast_process = subprocess.Popen(self.holster)

        # Stage starts at (x,y) = home when you boot up the VAST by default
        # It would be nice to query the stage directly, but not sure if this can be done...
        self.x_pos = 0
        self.y_pos = 0
        # Infinity motor, so abs theta pos is arbitrary!
        self.theta_pos = 0
        # NOTE: Keep positions in [um] and convert to uS under the hood!

        self.wait_until_done = False # Maybe implement this later...

        self.connect()

    def __del__(self):
        self.close()
        self.vast_process.kill() # Maybe don't just rudely kill the process... Is there a VAST.shutdown()?

    def close(self):
        self.f.close()
        
    def connect(self):
        connect_init = False

        print("Beginning VAST connection...")

        while not connect_init:
            try:
                self.f = open(r'\\.\pipe\VASTInteropPipe', 'r+b', 0)
                connect_init = True
            except Exception as e:
                print(e)
                time.sleep(1)
            
            print("Waiting for connection..." if not connect_init else "Connection established!")

    def get_current_position(self):
        return (
            self.x_pos,
            self.y_pos,
            self.theta_pos
        )

    def send(self, s):
        self.f.write(struct.pack('I', len(s)) + s.encode(encoding="ascii"))   # Write str length and str
        self.f.seek(0)                               # EDIT: This is also necessary
        print('Writing: ', s)
        n = struct.unpack('I', self.f.read(4))[0]    # Read str length
        s = self.f.read(n)                           # Read str
        self.f.seek(0)                               # Important!!!
        s.decode("ascii")
        print(f"Decoded:\t{s}")

    def start_vast(self):
        self.send('boot')

    def rotate(self, steps):
        self.send(
            f"rot,{steps}"
        )

    def rotate_deg(self, theta):
        self.theta_pos += theta # All rotation moves are relative...
        
        self.rotate(int(theta * VASTController.DEG_TO_US))

    def move_rel(self, x, y):
        self.send(
            f"mrel,{x},{y}"
        )
    
    def move_abs(self, x, y):
        self.send(
            f"mabs,{x},{y}"
        )

    def move_rel_um(self, x_um, y_um):
        self.x_pos += x_um
        self.y_pos += y_um

        self.move_rel(
            int(x_um * VASTController.UM_TO_US), 
            int(y_um * VASTController.UM_TO_US)
        )
    
    def move_abs_um(self, x_um, y_um):
        self.x_pos = x_um
        self.y_pos = y_um
        
        self.move_abs(
            int(x_um * VASTController.UM_TO_US), 
            int(y_um * VASTController.UM_TO_US)
        )
    
    def move_to_specified_position(self, x_pos=0.0, y_pos=0.0, theta_pos=0.0):
        # Move the stage first
        self.move_abs_um(x_um=x_pos, y_um=y_pos)

        print(f"vast_controller/move_to_specified_position : {(theta_pos)}")
        print(f"(theta_pos - self.theta_pos) : {(theta_pos - self.theta_pos)}")
        print(f"pre-rotation STP: {(self.theta_pos)}")
        # Do an "absolute" capillary rotation
        self.rotate_deg(
            theta=(theta_pos - self.theta_pos)
        )
        print(f"post-rotation STP: {(self.theta_pos)}")
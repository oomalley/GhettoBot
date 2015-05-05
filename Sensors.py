import threading
import subprocess
import datetime
import re
import math
from EventHook import EventHook

__author__ = 'oomadmin'


class Sensor(object):
    def __init__(self):
        print("init sensor")
        self.data = 0.0
        self.data_timestamp = datetime.datetime.now()

    def __repr__(self):
        return str(self.data) + " @ " + str(self.data_timestamp)

    def __str__(self):
        return str(self.data) + " @ " + str(self.data_timestamp)

    def read(self):
        return self.data, self.data_timestamp

    def format_correct(self, raw_data):
        return True

    def read_raw_data(self, driver_process):
        pass

    def extract_data(self, raw_data):
        pass


class ProximitySensor(Sensor):
    def __init__(self, warning_distance):
        Sensor.__init__(self)
        self.warning_distance = warning_distance
        self.onProximity = EventHook()

    def check_proximity(self):
        if self.data < self.warning_distance:
            self.onProximity.fire()


class InertialSensor(Sensor):
    def __init__(self):
        Sensor.__init__(self)
        self.pre_timestamp = datetime.datetime.now()
        self.onImpact = EventHook()
        self.onTilt = EventHook()
        self.onMove = EventHook()       # FixMe: assumes all movement is in horizontal plane
        self.A = []
        self.V = []
        self.X = []
        self.G = []

    def check_impact(self):
        pass

    def check_tilt(self):
        pass

    "@property"
    def acceleration(self):
        return self.A

    "@property"
    def velocity(self):
        return self.V

    "@property"
    def displacement(self):
        return self.X

    def speed(self):
        return math.sqrt(math.pow(self.V[0], 2) + math.pow(self.V[1],2) + math.pow(self.V[2]))

    def distance(self):
        return math.sqrt(math.pow(self.X[0], 2) + math.pow(self.X[1],2) + math.pow(self.X[2]))

    def bearing(self):
        if self.data[2] > 0:
            return self.data[2]
        else:
            return 360 + self.data[2]


class mpu9150(InertialSensor):
    def __init__(self):
        InertialSensor.__init__(self)
        cmd = "../linux-mpu9150-master/imu"
        self.driver_process = subprocess.Popen([cmd], bufsize=0, stdout=subprocess.PIPE)
        self.import_thread = threading.Thread(target=self.read_raw_data, args=(self.driver_process,))
        self.import_thread.daemon = True
        self.import_thread.start()

    def format_correct(self, raw_data):
        # re1 = '(X)'  # Any Single Character 1
        # re2 = '(:)'  # Any Single Character 2
        # re3 = '(\\s+)'  # White Space 1
        # re4 = '(-\\d+|\\d+)'  # Integer Number 1
        # re5 = '(\\s+)'  # White Space 2
        # re6 = '(Y)'  # Any Single Character 3
        # re7 = '(:)'  # Any Single Character 4
        # re8 = '(\\s+)'  # White Space 3
        # re9 = '(-\\d+|\\d+)'  # Integer Number 2
        # re10 = '(\\s+)'  # White Space 4
        # re11 = '(Z)'  # Any Single Character 5
        # re12 = '(:)'  # Any Single Character 6
        # re13 = '(\\s+)'  # White Space 5
        # re14 = '(-\\d+|\\d+)'  # Integer Number 3
        #
        # rg = re.compile(re1 + re2 + re3 + re4 + re5 + re6 + re7 + re8 + re9 + re10 + re11 + re12 + re13 + re14,
        #                 re.IGNORECASE | re.DOTALL)

        re1 = '(mX)'          # Word 1
        re2 = '(:)'           # Any Single Character 1
        re3 = '(\\s+)'        # White Space 1
        re4 = '(-\\d+|\\d+)'  # Integer Number 1
        re5 = '(\\s+)'        # White Space 2
        re6 = '(mY)'          # Word 2
        re7 = '(:)'           # Any Single Character 2
        re8 = '(\\s+)'        # White Space 3
        re9 = '.*?'           # Non-greedy match on filler
        re10 = '(-\\d+|\\d+)'     # Integer Number 2
        re11 = '(\\s+)'       # White Space 4
        re12 = '(mZ)'         # Word 3
        re13 = '(:)'          # Any Single Character 3
        re14 = '(\\s+)'       # White Space 5
        re15 = '(-\\d+|\\d+)'	    # Integer Number 3
        re16 = '(\\s+)'       # White Space 6
        re17 = '(aX)'         # Word 4
        re18 = '(:)'          # Any Single Character 4
        re19 = '(\\s+)'       # White Space 7
        re20 = '(-\\d+|\\d+)'     # Integer Number 4
        re21 = '(\\s+)'       # White Space 8
        re22 = '(aY)'         # Word 5
        re23 = '(:)'          # Any Single Character 5
        re24 = '(\\s+)'       # White Space 9
        re25 = '(-\\d+|\\d+)'	    # Integer Number 5
        re26 = '(\\s+)'       # White Space 10
        re27 = '(aZ)'         # Word 6
        re28 = '(:)'          # Any Single Character 6
        re29 = '(\\s+)'       # White Space 11
        re30 = '.*?'          # Non-greedy match on filler
        re31 = '(-\\d+|\\d+)'     # Integer Number 6

        rg = re.compile(re1+re2+re3+re4+re5+re6+re7+re8+re9+re10+re11+re12+re13+re14+re15+re16+re17+re18+re19+re20+re21+re22+re23+re24+re25+re26+re27+re28+re29+re30+re31,re.IGNORECASE|re.DOTALL)

        return rg.search(raw_data)

    def extract_data(self, raw_data):
        split_data = raw_data.split()
        self.data = float(split_data[5])
        self.pre_timestamp = self.data_timestamp
        self.data_timestamp = datetime.datetime.now()
        dt = (self.data_timestamp - self.pre_timestamp).total_seconds()
        alpha = 0.1
        raw_accel = (int(split_data[7]), int(split_data[9]), int(split_data[11]))
        new_accel = [0, 0, 0]
        new_vel = [0, 0, 0]
        new_disp = [0, 0, 0]

        # Use low pass filer to get gravity vector
        self.G[0] = alpha * self.G[0] + (1 - alpha) * raw_accel[0]
        self.G[1] = alpha * self.G[1] + (1 - alpha) * raw_accel[1]
        self.G[2] = alpha * self.G[2] + (1 - alpha) * raw_accel[2]

        new_accel[0] = raw_accel[0] - self.G[0]
        new_accel[1] = raw_accel[1] - self.G[1]
        new_accel[2] = raw_accel[2] - self.G[2]

        new_vel[0] = self.V[0] + (0.5 * dt * (new_accel[0] + self.A[0]))
        new_vel[1] = self.V[1] + (0.5 * dt * (new_accel[1] + self.A[1]))
        new_vel[2] = self.V[2] + (0.5 * dt * (new_accel[2] + self.A[2]))

        new_disp[0] = self.X[0] + (0.5 * dt * (new_vel[0] + self.V[0]))
        new_disp[1] = self.X[1] + (0.5 * dt * (new_vel[1] + self.V[1]))
        new_disp[2] = self.X[2] + (0.5 * dt * (new_vel[2] + self.V[2]))

        self.A = new_accel
        self.V = new_vel
        self.X = new_disp

        ## print("Extracted data: " + str(self.data))

    def read_raw_data(self, driver_process):
        raw_data = ""
        for line in iter(driver_process.stdout.readline, ""):
            # print("[" + line.strip() + "]")
            raw_data = str(line.strip())
            # print("Read Raw: " + raw_data)
            if self.format_correct(raw_data):
                # print("Match: " + raw_data)
                try:
                    self.extract_data(raw_data)
                    if sum(self.V) > 0:             # Fixme: may need to smooth velocity (low pass filter?)
                        self.OnMove.fire(self.X)
                except Exception as e:
                    print("Error: " + str(e))
        return


class Hcsr04(ProximitySensor):
    def __init__(self, warning_distance):
        ProximitySensor.__init__(self, warning_distance)
        cmd = "./hcsr04"
        # self.last_distance = 0.0
        # self.last_distance_timestamp = datetime.datetime.timestamp()
        self.driver_process = subprocess.Popen([cmd], bufsize=0, stdout=subprocess.PIPE)
        self.import_thread = threading.Thread(target=self.read_raw_data(self.driver_process))
        self.import_thread.daemon = True
        self.import_thread.start()

    def read_raw_data(self, driver_process):
        # print("starting data import")

        for line in iter(self.driver_process.stdout.readline, ""):
            # print("[" + line.strip() + "]")
            try:
                # dist=str(float(line.strip()))
                # print("Dist: " + dist)
                self.data = float(line.strip())
                self.data_timestamp = datetime.datetime.now()
                self.check_proximity()

            except Exception as e:
                print("Error: " + str(e))
        return

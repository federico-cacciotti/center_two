import serial

NAK = b'\x15' # negative acknowledge
ACK = b'\x06' # acknowledge
ENQ = b'\x05' # enquiry
CR =  b'\x0d' # carriage return
LF =  b'\x0a' # line feed

# error strings
ACK_ERROR = "Acknowlegment error"
UNKNOWN_ERROR = "Unknown error"
INCORRECT_VALUE_ERROR = "Incorrect value"

# sensor status strings
SENS_OK = "Measurement data ok"
SENS_UR = "Measurement under range"
SENS_OV = "Measurement over range"
TRANS_ERR = "Transmitter error"
TRANS_OFF = "Transmitter switched off"
NO_TRANS = "No transmitter"
ID_ERR = "Identification error"
ITR_ER = "ITR error"

# error status strings
DEV_ERR = "Device error"
HW_ERR = "Hardware error (FAIL illum.)"
INV_PAR = "Invalid parameter"
STX_ERR = "Syntax error"
NO_ERR = "No error"

class Controller():

    def __init__(self, serial_port, baudrate=9600, pariy=serial.PARITY_NONE, stopbits=2):
        self.serial_com = serial.Serial(port=serial_port, baudrate=baudrate, timeout=1, parity=serial.PARITY_NONE, stopbits=2)

    def closeCommunication(self):
        self.serial_com.close()
    
    def sendCommand(self, command):
        return self.serial_com.write(command+CR+LF)
    
    def enquiry(self):
        self.serial_com.write(ENQ)
        return self.serial_com.readline().rstrip().decode()
    
    def readLine(self):
        return self.serial_com.readline()
    
    def readAcknowledgement(self):
        return self.serial_com.readline().rstrip()

    def checkSensorStatus(self, status):
        if status == 0:
            return SENS_OK
        elif status == 1:
            return SENS_UR
        elif status == 2:
            return SENS_OR
        elif status == 3:
            return TRANS_ERR
        elif status == 4:
            return TRANS_OFF
        elif status == 5:
             return NO_TRANS
        elif status == 6:
            return ID_ERR
        elif status == 7:
            return ITR_ERR
        else:
            return -1

    # AOM
    def setAnalogOutput(self, channel, curve):
        """
        Set analog output mode. Characteristic curve of the recorder output.

        Parameters:
        channel (int): 0 for channel 1, 1 for channel 2, 2 for channel 3.
        curve (int): 0 for LoG, 1 for LoG A, 2 for LoG -6, 3 for LoG -3, 4 for LoG +0, 
                     5 for LoG +3, 6 LoGC1, 7 for LoGC2, 8 for LoGC3, 9...22 for Lin -10...Lin +3,
                     23 for IM221, 24 for LoGC4, 25 for PM411.
        """
        command = ("AOM,{:d},{:d}".format(channel, curve)).encode()
        if self.readAcknowledgement() == ACK:
            r_channel, r_curve = self.enquiry().split(",")
            r_channel = int(r_channel)
            r_curve = int(r_curve)
            if r_channel == channel and r_curve == curve:
                print("Analog output successfully set")
                return [r_channel, r_curve]
            else:
                print(UNKNOWN_ERROR)
                return -1
        else:
            print(ACK_ERROR)
            return -1
            

    # BAU
    def setBaudrate(self, mode=0):
        """
        Baudrate. Transfer rate of the RS232C interface.

        Parameters:
        mode (int): 0 for 9600 (default), 1 for 19200, or 2 for 38400.
        """
        if mode == 0 or mode == 1 or mode == 2:
            command = ("BAU,{:d}".format(mode)).encode()
        else:
            print(INCORRECT_VALUE_ERROR)
            return -1
            
        self.sendCommand(command)
        if self.readAcknowledgement() == ACK:
            r_mode = int(self.enquiry())
            if r_mode == mode:
                print("Baudrate succesfully set")
                return r_mode
            else:
                print(UNKNOWN_ERROR)
                return -1
        else:
            print(ACK_ERROR)
            return -1
            
    # COM
    def setContinuousMode(self, period=1):
        """
        TO DO
        Continuous mode. Continuous transmission of measurements to the serial interface.

        Parameters:
        period (int): 0 for 100 milliseconds, 1 for 1 second (default), 2 for 1 minute.
        """
        command = ("COM,{:d}".format(period)).encode()
        self.sendCommand(command)
        if self.readAcknowledgement() == ACK:
            s, v = self.enquiry().split(", ")
            # TO DO
        else:
            print(ACK_ERROR)
            return -1

    # CORR
    def setCorrectionFactor(self, cr1=1.0, cr2=1.0, cr3=1.0):
        """
        Correction factors.

        Parameters:
        cr1 (float): correction factor of channel 1, 0.10 to 9.99.
        cr2 (float): correction factor of channel 2, 0.10 to 9.99.
        cr3 (float): correction factor of channel 3, 0.10 to 9.99.
        """
        if cr1 < 0.1 or cr1 > 9.99:
            print(INCORRECT_VALUE_ERROR)
            return -1
        if cr2 < 0.1 or cr3 > 9.99:
            print(INCORRECT_VALUE_ERROR)
            return -1
        if cr2 < 0.1 or cr3 > 9.99:
            print(INCORRECT_VALUE_ERROR)
            return -1
        command = ("COR,{:.2f},{:.2f},{:.2f}".format(cr1, cr2, cr3)).encode()
        self.sendCommand(command)
        if self.readAcknowledgement() == ACK:
            r_cr1, r_cr2, r_cr3 = self.enquiry().split(",")
            r_cr1 = float(r_cr1)
            r_cr2 = float(r_cr2)
            r_cr3 = float(r_cr3)
            return [r_cr1, r_cr2, r_cr3]
        else:
            print(ACK_ERROR)
            return -1

    # DCD
    def setNumberOfDigits(self, digits=2):
        """
        Number of digits shown on the display

        Parameters:
        digits (int): 2 for 2 digits (default), 3 for 3 digits.
        """
        if digits == 2 or digits == 3:
            command = ("DCD,{:d}".format(digits)).encode()
        else:
            print(INCORRECT_VALUE_ERROR)
            return -1
            
        self.sendCommand(command)
        if self.readAcknowledgement() == ACK:
            r_digits = int(self.enquiry())
            if r_digits == digits:
                print("Display digits succesfully set")
                return r_digits
            else:
                print(UNKNOWN_ERROR)
                return -1
        else:
            print(ACK_ERROR)
            return -1

    # DGS

    # ERA

    # ERR
    def getErrorStatus(self):
        """
        Error status.

        Parameters:
        None
        """
        command = b"ERR"
        self.sendCommand(command)
        if self.readAcknowledgement() == ACK:
            errors = []
            status = self.enquiry()
            if status[0] == '1':
                errors.append(DEV_ERR)
            if status[1] == '1':
                errors.append(HW_ERR)
            if status[2] == '1':
                errors.append(INV_PAR)
            if status[3] == '1':
                errors.append(STX_ERR)
            if status == '0000':
                errors.append(NO_ERR)
            return [status, errors]
        else:
            print(ACK_ERROR)
            return -1

    # EUM

    # FIL

    # FSR

    # FUM

    # GAS

    # HVC

    # ITR

    # LOC

    # OFC

    # OFD

    # PNR
    def getProgramNumber(self):
        """
        Firmware version number.

        Parameters:
        None
        """
        command = b"PNR"
        self.sendCommand(command)
        if self.readAcknowledgement() == ACK:
            return self.enquiry()
        else:
            print(ACK_ERROR)
            return -1

    # PR#
    def getChannelPressure(self, channel):
        """
        Pressure reading of sensor #.

        Parameters:
        channel (int): 1 for channel 1, 2 for channel 2, 3 for channel 3.
        """
        if channel == 1 or channel == 2 or channel == 3:
            command = ("PR{:d}".format(channel)).encode()
            self.sendCommand(command)
        else:
            print(INCORRECT_VALUE_ERROR)
            return -1
        if self.readAcknowledgement() == ACK:
            s, v = self.enquiry().split(",")
            s = int(s)
            value = float(v)
            status = self.checkSensorStatus(s)
            return [status, value]
        else:
            print(ACK_ERROR)
            return -1

    # PRE
    def setPiraniRangeExtention(self, re1=0, re2=0, re3=0):
        """
        Pirani range extension.

        Parameters:
        re1 (int): range extension for transmitter 1, 0 for Off (default), 1 for On.
        re2 (int): same for above.
        re3 (int): same for above.
        """
        if (re1 == 0 or re1 == 1) and (re2 == 0 or re2 == 1) and (re3 == 0 or re3 == 1):
            command = ("PRE,{:d},{:d},{:d}".format(re1, re2, re3)).encode()
            self.sendCommand(command)
        else:
            print(INCORRECT_VALUE_ERROR)
            return -1
        if self.readAcknowledgement() == ACK:
            r_re1, r_2, r_re3 = self.enquiry().split(",")
            r_re1 = int(r_re1)
            r_re2 = int(r_re2)
            r_re3 = int(r_re3)

            if r_re1 == re1 and r_re2 == re2 and r_re3 == re3:
                print("Pirani range extension successfully set")
                return [re1, re2, re3]
            else:
                print(UNKNOWN_ERROR)
                return -1
        else:
            print(ACK_ERROR)
            return -1

    # PRX
    def getPressure(self):
        """
        Pressure reading of all transmitters.

        Parameters:
        None
        """
        command = b"PRX"
        self.sendCommand(command)
        if self.readAcknowledgement() == ACK:
            status = [[], [], []]
            value = [[], [], []]
            status[0], value[0], status[1], value[1], status[2], value[2] = self.enquiry().split(",")
            for i, (s, v) in enumerate(zip(status, value)):
                status[i] = self.checkSensorStatus(int(s))
                value[i] = float(v)
            return [status, value]
        else:
            print(ACK_ERROR)
            return -1

    # RES

    # SAV

    # SC#

    # SP#

    # SPS

    # TAD

    # TDI

    # TEE

    # TEP
    
    # TID
    def getTransmitterId(self):
        """
        Transmitter identification.

        Parameters:
        None
        """
        command = b"TID"
        self.sendCommand(command)
        if self.readAcknowledgement() == ACK:
            return self.enquiry().split(",")
        else:
            print(ACK_ERROR)
            return -1

    # TIO

    # TKB

    # TLC

    # TRA

    # TRS

    # UNI

    # WDT
    
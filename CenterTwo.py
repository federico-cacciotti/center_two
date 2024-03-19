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
            returned_mode = self.enquiry()
            if returned_mode == mode:
                print("Baudrate succesfully set")
                return returned_mode
            else:
                print(UNKNOWN_ERROR)
                return -1
        else:
            print(ACK_ERROR)
            return -1
    # COM
    def setContinuousMode(self, period=1):
        """
        Continuous mode. Continuous transmission of measurements to the serial interface.

        Parameters:
        period (int): 0 for 100 milliseconds, 1 for 1 seconds (default), 2 for 1 minute.
        """
        command = ("COM,{:d}".format(period)).encode()
        self.sendCommand(command)
        if self.readAcknowledgement() == ACK:
            s, v = self.enquiry().split(", ")
        else:
            print(ACK_ERROR)

    # ERR
    def getErrorStatus(self):
        command = b"ERR"
        self.sendCommand(command)
        if self.readAcknowledgement() == ACK:
            errors = []
            status = self.enquiry()
            if status[0] == '1':
                errors.append("Device error")
            if status[1] == '1':
                errors.append("Hardware error (FAIL illum.)")
            if status[2] == '1':
                errors.append("Invalid parameter")
            if status[3] == '1':
                errors.append("Syntax error")
            if status == '0000':
                errors.append("No error")
            return status, errors
        else:
            print(ACK_ERROR)
            return -1

    # PNR
    def getProgramNumber(self):
        command = b"PNR"
        self.sendCommand(command)
        if self.readAcknowledgement() == ACK:
            return self.enquiry()

    # TID
    def getTransmitterId(self):
        command = b"TID"
        self.sendCommand(command)
        if self.readAcknowledgement() == ACK:
            return self.enquiry().split(", ")
    
    # PR#
    def getChannelPressure(self, channel):
        command = ("PR{:d}".format(channel)).encode()
        self.sendCommand(command)
        if self.readAcknowledgement() == ACK:
            s, v = self.enquiry().split(", ")
            s = int(s)
            v = float(v)
            status = self.checkSensorStatus(s)
            return [status, value]
        else:
            print("Error while reading sensor")
            return -1
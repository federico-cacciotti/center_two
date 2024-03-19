import serial

NAK = b'\x15' # negative acknowledge
ACK = b'\x06' # acknowledge
ENQ = b'\x05' # enquiry
CR =  b'\x0d' # carriage return
LF =  b'\x0a' # line feed

class Controller():

    def __init__(self, serial_port, baudrate=9600, pariy=serial.PARITY_NONE, stopbits=2):
        self.serial_com = serial.Serial(port=serial_port, baudrate=baudrate, timeout=1, parity=serial.PARITY_NONE, stopbits=2)

    def closeCommunication(self):
        self.serial_com.close()
    
    def sendCommand(self, command):
        return self.serial_com.write(command+CR+LF)
    
    def enquiry(self):
        self.serial_com.write(ENQ)
    
    def readLine(self):
        return self.serial_com.readline()
    
    def readAcknowledgement(self):
        return self.serial_com.readline().rstrip()

    # BAU
    def setBaudrate(self, mode):
        """
        mode (int): 0 for 9600, 1 for 19200, or 2 for 38400
        """
        if mode == 0 or mode == 1 or mode == 2:
            command = ("BAU,{:d}".format(mode)).encode()
        else:
            print("Incorrect baudrate")
            return -1
            
        self.sendCommand(command)
            if self.readAcknowledgement() == ACK:
                self.enquiry()
                returned_mode = int(self.readLine().rstrip().decode())
                if returned_mode == mode:
                    print("Baudrate succesfully set")
                    return returned_mode
                else:
                    print("Unknown error")
                    return -1

    # ERR
    def getErrorStatus(self):
        command = b"ERR"
        self.sendCommand(command)
        if self.readAcknowledgement() == ACK:
            self.enquiry()
            errors = []
            status = self.readLine().rstrip().decode()
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

    # PNR
    def getProgramNumber(self):
        command = b"PNR"
        self.sendCommand(command)
        if self.readAcknowledgement() == ACK:
            self.enquiry()
            return self.readLine().rstrip().decode()

    # TID
    def getTransmitterId(self):
        command = b"TID"
        self.sendCommand(command)
        if self.readAcknowledgement() == ACK:
            self.enquiry()
            return self.readLine().rstrip().decode().split(", ")
    
    # PR#
    def getPressure(self, channel):
        command = ("PR{:d}".format(channel)).encode()
        self.sendCommand(command)
        if self.readAcknowledgement() == ACK:
            self.enquiry()
            status, value = self.readLine().rstrip().decode().split(", ")
            status = int(status)
            value = float(value)
            
            if status == 1:
                print("Measurement under range")
            elif status == 2:
                print("Measurement over range")
            elif status == 3:
                print("Transmitter error")
            elif status == 4:
                print("Transmitter switched off")
            elif status == 5:
                print("No transmitter")
            elif status == 6:
                print("Identification error")
            elif status == 7:
                print("ITR error")
    
            return [status, value]
                
        else:
            print("Error while reading sensor")
            return -1
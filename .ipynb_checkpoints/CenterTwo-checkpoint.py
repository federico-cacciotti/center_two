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
SENS_STATUS = ["Measurement data ok",
               "Measurement under range",
               "Measurement over range",
               "Transmitter error",
               "Transmitter switched off",
               "No transmitter",
               "Identification error",
               "ITR error"]

# error status strings
DEV_ERR = "Device error"
HW_ERR = "Hardware error (FAIL illum.)"
INV_PAR = "Invalid parameter"
STX_ERR = "Syntax error"
NO_ERR = "No error"

# queued error strings
QUEUED_ERROR = ["No error",
                "Watchdog has triggered",
                "Task(s) not executed",
                "EPROM error",
                "RAM error",
                "EEPROM error",
                "Display error",
                "A/D converter error",
                "UART error",
                "Transmitter 1 general error",
                "Transmitter 1 ID error",
                "Transmitter 2 general error",
                "Transmitter 2 ID error",
                "Transmitter 3 general error",
                "Transmitter 3 ID error"]

class Controller():

    def __init__(self):
        self.is_connected = False
        self.serial_port = None
        self.baudrate = None

    def connect(self, serial_port, baudrate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_TWO):
        self.serial_port = serial_port
        self.baudrate = baudrate
        try:
            self.serial_com = serial.Serial(port=serial_port, baudrate=baudrate, timeout=1, parity=parity, stopbits=stopbits)
            self.is_connected = True
        except serial.SerialException:
            print("Could not open serial port")
            self.is_connected = False
            pass

    def close(self):
        self.serial_com.close()
        self.is_connected = False
    
    def send_command(self, command):
        return self.serial_com.write(command+CR+LF)
    
    def enquiry(self):
        self.serial_com.write(ENQ)
        return self.serial_com.readline().rstrip().decode()
    
    def read_line(self):
        return self.serial_com.readline()
    
    def read_acknowledgement(self):
        return self.serial_com.readline().rstrip()

    # AOM
    def set_analog_output(self, channel, curve):
        """
        Set analog output mode. Characteristic curve of the recorder output.

        Parameters:
        channel (int): 0 for channel 1, 1 for channel 2, 2 for channel 3.
        curve (int): 0 for LoG, 1 for LoG A, 2 for LoG -6, 3 for LoG -3, 4 for LoG +0, 
                     5 for LoG +3, 6 LoGC1, 7 for LoGC2, 8 for LoGC3, 9...22 for Lin -10...Lin +3,
                     23 for IM221, 24 for LoGC4, 25 for PM411.
        """
        command = ("AOM,{:d},{:d}".format(channel, curve)).encode()
        if self.read_acknowledgement() == ACK:
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
    def set_baudrate(self, mode=0):
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
            
        self.send_command(command)
        if self.read_acknowledgement() == ACK:
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
    def set_continuous_mode(self, period=1):
        """
        TO DO
        Continuous mode. Continuous transmission of measurements to the serial interface.

        Parameters:
        period (int): 0 for 100 milliseconds, 1 for 1 second (default), 2 for 1 minute.
        """
        command = ("COM,{:d}".format(period)).encode()
        self.send_command(command)
        if self.read_acknowledgement() == ACK:
            s, v = self.enquiry().split(", ")
            # TO DO
        else:
            print(ACK_ERROR)
            return -1

    # CORR
    def set_correction_factor(self, cr1=1.0, cr2=1.0, cr3=1.0):
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
        self.send_command(command)
        if self.read_acknowledgement() == ACK:
            r_cr1, r_cr2, r_cr3 = self.enquiry().split(",")
            r_cr1 = float(r_cr1)
            r_cr2 = float(r_cr2)
            r_cr3 = float(r_cr3)
            return [r_cr1, r_cr2, r_cr3]
        else:
            print(ACK_ERROR)
            return -1

    # DCD
    def set_number_of_digits(self, digits=2):
        """
        Number of digits shown on the display

        Parameters:
        digits (int): 2 for 2 digits (default), 3 for 3 digits.
        """
        if digits == 2 or digits == 3:
            command = ("DCD,{:d}".format(digits)).encode()
            self.send_command(command)
        else:
            print(INCORRECT_VALUE_ERROR)
            return -1
            
        if self.read_acknowledgement() == ACK:
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
    def get_error_status(self):
        """
        Error status.

        Parameters:
        None
        """
        command = b"ERR"
        self.send_command(command)
        if self.read_acknowledgement() == ACK:
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
    def get_program_number(self):
        """
        Firmware version number.

        Parameters:
        None
        """
        command = b"PNR"
        self.send_command(command)
        if self.read_acknowledgement() == ACK:
            return self.enquiry()
        else:
            print(ACK_ERROR)
            return -1

    # PR#
    def get_channel_pressure(self, channel):
        """
        Pressure reading of sensor #.

        Parameters:
        channel (int): 1 for channel 1, 2 for channel 2, 3 for channel 3.
        """
        if channel == 1 or channel == 2 or channel == 3:
            command = ("PR{:d}".format(channel)).encode()
            self.send_command(command)
        else:
            print(INCORRECT_VALUE_ERROR)
            return -1
        if self.read_acknowledgement() == ACK:
            s, v = self.enquiry().split(",")
            s = int(s)
            value = float(v)
            status = SENS_STATUS[s]
            return [status, value]
        else:
            print(ACK_ERROR)
            return -1

    # PRE
    def set_pirani_pange_extention(self, re1=0, re2=0, re3=0):
        """
        Pirani range extension.

        Parameters:
        re1 (int): range extension for transmitter 1, 0 for Off (default), 1 for On.
        re2 (int): same for above.
        re3 (int): same for above.
        """
        if (re1 == 0 or re1 == 1) and (re2 == 0 or re2 == 1) and (re3 == 0 or re3 == 1):
            command = ("PRE,{:d},{:d},{:d}".format(re1, re2, re3)).encode()
            self.send_command(command)
        else:
            print(INCORRECT_VALUE_ERROR)
            return -1
        if self.read_acknowledgement() == ACK:
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
    def get_pressure(self):
        """
        Pressure reading of all transmitters.

        Parameters:
        None
        """
        command = b"PRX"
        self.send_command(command)
        if self.read_acknowledgement() == ACK:
            status = [[], [], []]
            value = [[], [], []]
            status[0], value[0], status[1], value[1], status[2], value[2] = self.enquiry().split(",")
            for i, (s, v) in enumerate(zip(status, value)):
                status[i] = SENS_STATUS[int(s)]
                value[i] = float(v)
            return [status, value]
        else:
            print(ACK_ERROR)
            return -1

    # RES
    def reset_serial(self, rst=0):
        """
        Reset the serial interface and deletes the input buffer. All queued errors messages are sent to the host.

        Parameters:
        rst (int): if 1 performs a reset.
        """
        if rst == 1:
            command = ("RES,{:d}".format(rst)).encode()
            self.send_command(command)
        else:
            print("To perform a reset the rst parameter must be 1")
            return -1
        if self.read_acknowledgement() == ACK:
            quequed_errors = self.enquiry().split(",")
            quequed_errors = [int(x) for x in quequed_errors]
            return [QUEUED_ERROR[x] for x in quequed_errors]
        else:
            print(ACK_ERROR)
            return -1

    # SAV

    # SC#

    # SP#

    # SPS

    # TAD

    # TDI

    # TEE

    # TEP
    
    # TID
    def get_transmitter_id(self):
        """
        Transmitter identification.

        Parameters:
        None
        """
        command = b"TID"
        self.send_command(command)
        if self.read_acknowledgement() == ACK:
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
    
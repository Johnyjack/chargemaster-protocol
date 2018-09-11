import usb1
import binascii
import time
from analyzeReply import *

class BatteryData:
    """ Handles and stores battery data """
    def __init__(self, battery_chem, series_cells, batt_capacity, usb_device_handle):
        self.chemistry = battery_chem
        self.series_cells = series_cells
        self.capacity = batt_capacity
        self.handle = usb_device_handle
        self.is_logging = False
        self.is_running_action = False

        self.data = {
            'battery_voltage': 0,
            'battery_current': 0,
            'cell1_voltage': 0,
            'cell2_voltage': 0,
            'cell3_voltage': 0,
            'cell4_voltage': 0,
            'cell5_voltage': 0,
            'cell6_voltage': 0,
            'capacity_change': 0,
            'temp': 0,
            'run_time': 0,
            'is_running': 0,
            }
        self.battery_voltage = 0
        self.battery_current = 0
        self.cell1_voltage = 0
        self.cell2_voltage = 0
        self.cell3_voltage = 0
        self.cell4_voltage = 0
        self.cell5_voltage = 0
        self.cell6_voltage = 0
        self.capacity_change = 0
        self.temp = 0
        self.run_time = 0
        self.is_running = 0

    def load_action(self, action):
        if action == 'balance charge':
            self.current_action = action
            return True
        elif action == 'charge':
            self.current_action = action
            return True
        elif action == 'fast charge':
            self.current_action = action
            return True
        elif action == 'discharge':
            self.current_action = action
            return True
        elif action == 'storage':
            self.current_action = action
            return True
        else:
            print 'unknown action'
            return False

    def log_data(self):

    def get_response(command_str, handle):
        timeoutms = 100
        if command_str=='5a':
            command = binascii.unhexlify('0f035a005affff0000000000000000000000000000000000000000000000000000000000000000000000000'
                                  '00000000000000000000000000000000000000000')
        #if command_str=='5f':
        #if command_str=='05':
        if command_str=='55':
            command = binascii.unhexlify('0f03550055ffff0000000000000000000000000000000000000000000000000000000000000000000000000'
                                  '00000000000000000000000000000000000000000')
        #if command_str=='57':
        #if command_str=='fe':
        sent = handle.interruptWrite(1, command, timeoutms)
        print 'Nr. bytes sent:', sent
        response = handle.interruptRead(1, 64)
        return response

    def transaction_55(result): #still need to find current
        header_byte = binascii.b2a_hex(result[0:1])
        packet_lenth = binascii.b2a_hex(result[1:2])
        transaction_type = binascii.b2a_hex(result[2:3])
        unknown1 = binascii.b2a_hex(result[3:4])
        is_running = int(binascii.b2a_hex(result[4:5]), 16) #2 = standbye, 1 = charging
        capacity_change = int(binascii.b2a_hex(result[5:7]), 16) #mAh
        run_time = int(binascii.b2a_hex(result[7:9]), 16) #seconds
        batt_voltage = int(binascii.b2a_hex(result[9:11]), 16) #in mV
        batt_current = int(binascii.b2a_hex(result[11:13]), 16) #mA

        print 'unknown1: ', binascii.b2a_hex(result[13:14])

        internal_temp = int(binascii.b2a_hex(result[14:15]), 16) #in C
        cell1_voltage = int(binascii.b2a_hex(result[17:19]), 16) #in mV
        cell2_voltage = int(binascii.b2a_hex(result[19:21]), 16) #in mV
        cell3_voltage = int(binascii.b2a_hex(result[21:23]), 16) #in mV
        cell4_voltage = int(binascii.b2a_hex(result[23:25]), 16) #in mV
        cell5_voltage = int(binascii.b2a_hex(result[25:27]), 16) #in mV
        cell6_voltage = int(binascii.b2a_hex(result[27:29]), 16) #in mV
        
        print 'unknown2: ', binascii.b2a_hex(result[29:])

        if header_byte != '0f':
            print colored('Header not correct! Aborting decoding. Received: ' + header_byte, 'red')
            return

        if packet_lenth != '22':
            print colored('Unexpected packet length! Aborting decoding. Received: ' + packet_lenth, 'red')
            return

        if transaction_type != '55':
            print colored('Wrong transaction type! Aborting decoding. Received: ' + transaction_type, 'red')
            return

        if unknown1 != '00':
            print colored('!!! Values changed !!! previous: 00', 'red')


        if binascii.b2a_hex(result[36:38]) != 'ffff':
            print colored('Stop sign not correct! Aborting decoding. Received: ' + binascii.b2a_hex(result[39:41]), 'red')
            return

    def transaction_5a(result):

        if binascii.b2a_hex(result[0:1]) != '0f':
            print colored('Header not correct! Aborting decoding. Received: ' + binascii.b2a_hex(result[0]), 'red')
            return

        packetlength = struct.unpack('B', result[1:2])[0]
        if packetlength != 37:
            print colored('Unexpected packet length! Aborting decoding. Received: ' + binascii.b2a_hex(result[1]), 'red')
            return

        if binascii.b2a_hex(result[2:3]) != '5a':
            print colored('Wrong transaction type! Aborting decoding. Received: ' + binascii.b2a_hex(result[2]), 'red')
            return

        unknown1 = binascii.b2a_hex(result[3:4])
        print 'Unknown field Nr. 1:', unknown1
        if unknown1 != '00':
            print colored('!!! Values changed !!! previous: 00', 'red')

        resttime = struct.unpack('B', result[4:5])[0]
        print 'Resttime:', resttime, 'minutes'

        temp = struct.unpack('B', result[5:6])[0]
        if temp == 1:
            saftytimerenable = True
        else:
            saftytimerenable = False
        print 'Safty Timer Enable:', saftytimerenable
        saftytimertimeout = struct.unpack('>H', result[6:8])[0]
        print 'Safty Timer Timeout:', saftytimertimeout, 'minutes'

        temp = struct.unpack('B', result[8:9])[0]
        if temp == 1:
            capacitycutoutenable = True
        else:
            capacitycutoutenable = False
        print 'Capacity Cutout Enable:', capacitycutoutenable
        capacitycutoutvalue = struct.unpack('>H', result[9:11])[0]
        print 'Capacity Cutout Value:', capacitycutoutvalue, 'mAh'

        temp = struct.unpack('B', result[11:12])[0]
        if temp == 1:
            keybeepenable = True
        else:
            keybeepenable = False
        print 'Keybeep Enable:', keybeepenable

        temp = struct.unpack('B', result[12:13])[0]
        if temp == 1:
            buzzerenabled = True
        else:
            buzzerenabled = False
        print 'Buzzer Enable:', buzzerenabled

        inputcutoff = float(struct.unpack('>H', result[13:15])[0])/1000
        print 'Input Cutoff Voltage:', inputcutoff, 'V'

        unknown2 = binascii.b2a_hex(result[15:18])
        print 'Unknown field Nr. 2:', unknown2
        if unknown2 != '0000':
            print colored('!!! Values changed !!! previous: 0000', 'red')

        #jacks edits
        current = float(struct.unpack('>H', result[16:18])[0])/1000
        print 'Current: ', current, 'A'

        protectiontemp = struct.unpack('B', result[17:18])[0]
        print 'Protection Temperature:', protectiontemp, 'degrees'

        batteryvoltage = float(struct.unpack('>H', result[18:20])[0])/1000
        print 'Battery Voltage:', batteryvoltage, 'V'

        cell1voltage = float(struct.unpack('>H', result[20:22])[0])/1000
        print 'Cell 1 Voltage:', cell1voltage, 'V'

        cell2voltage = float(struct.unpack('>H', result[22:24])[0])/1000
        print 'Cell 2 Voltage:', cell2voltage, 'V'

        cell3voltage = float(struct.unpack('>H', result[24:26])[0])/1000
        print 'Cell 3 Voltage:', cell3voltage, 'V'

        cell4voltage = float(struct.unpack('>H', result[26:28])[0])/1000
        print 'Cell 4 Voltage:', cell4voltage, 'V'

        cell5voltage = float(struct.unpack('>H', result[28:30])[0])/1000
        print 'Cell 5 Voltage:', cell5voltage, 'V'

        cell6voltage = float(struct.unpack('>H', result[30:32])[0])/1000
        print 'Cell 6 Voltage:', cell6voltage, 'V'

        unknown3 = binascii.b2a_hex(result[32:38])
        print 'Unknown field Nr. 3:', unknown3
        if unknown3 != '000000000000':
            print colored('!!! Values changed !!! previous: 000000000000', 'red')

        unknown4 = binascii.b2a_hex(result[38:39])
        print colored('Unknown field Nr. 4: ' + str(unknown4) + ' (changes)', 'yellow')

        if binascii.b2a_hex(result[39:41]) != 'ffff':
            print colored('Stop sign not correct! Aborting decoding. Received: ' + binascii.b2a_hex(result[39:41]), 'red')
            return

        #print '\nData received:'
        print binascii.b2a_hex(result)

        #def start_action(self):
            return True
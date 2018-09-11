import usb1
import binascii
import time
import csv
import sys
from pathlib import Path
import os.path

class BatteryClass:
    """ Handles and stores battery data """
    def __init__(self, battery_chem, series_cells, batt_capacity, usb_device_handle, log_filename):
        self.chemistry = battery_chem
        self.series_cells = series_cells
        self.capacity = batt_capacity
        self.usb_device_handle = usb_device_handle
        self.is_logging = False
        self.action_state = False
        self.log_filename = ('%s.csv' % log_filename)
        print self.log_filename
        self.transaction_requested = '55'

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
        self.action_state = 0
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
            'action_state': 0,
            }

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

    def get_data(self):
        self.result = self.get_response(self.transaction_requested, self.usb_device_handle)
        if self.transaction_requested == '55':   
            self.proces_55_data()
            self.data = {
                'battery_voltage': self.battery_voltage,
                'battery_current': self.battery_current,
                'cell1_voltage': self.cell1_voltage,
                'cell2_voltage': self.cell2_voltage,
                'cell3_voltage': self.cell3_voltage,
                'cell4_voltage': self.cell4_voltage,
                'cell5_voltage': self.cell5_voltage,
                'cell6_voltage': self.cell6_voltage,
                'capacity_change': self.capacity_change,
                'temp': self.temp,
                'run_time': self.run_time,
                'action_state': self.action_state,
                }

    def log_data_header(self):
        with open(self.log_filename,'a') as f:
            w = csv.writer(f)
            debug_w = csv.writer(sys.stderr)
            w.writerow(self.data.keys())
            debug_w.writerow(self.data.keys())


    def log_data(self):
        with open(self.log_filename,'a') as f:
            w = csv.writer(f)
            debug_w = csv.writer(sys.stderr)
            w.writerow(self.data.values())
            debug_w.writerow(self.data.values())

    def get_response(self, command_str, handle):
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
        response = handle.interruptRead(1, 64)
        return response

    def proces_55_data(self): #still need to find current
        self.header_byte = binascii.b2a_hex(self.result[0:1])
        self.packet_lenth = binascii.b2a_hex(self.result[1:2])
        self.transaction_type = binascii.b2a_hex(self.result[2:3])
        self.unknown1 = binascii.b2a_hex(self.result[3:4])
        self.action_state = int(binascii.b2a_hex(self.result[4:5]), 16) #2 = standbye, 1 = charging
        self.capacity_change = int(binascii.b2a_hex(self.result[5:7]), 16) #mAh
        self.run_time = int(binascii.b2a_hex(self.result[7:9]), 16) #seconds
        self.battery_voltage = int(binascii.b2a_hex(self.result[9:11]), 16) #in mV
        self.battery_current = int(binascii.b2a_hex(self.result[11:13]), 16) #mA

        #print 'unknown1: ', binascii.b2a_hex(self.result[13:14])

        self.temp = int(binascii.b2a_hex(self.result[14:15]), 16) #in C
        self.cell1_voltage = int(binascii.b2a_hex(self.result[17:19]), 16) #in mV
        self.cell2_voltage = int(binascii.b2a_hex(self.result[19:21]), 16) #in mV
        self.cell3_voltage = int(binascii.b2a_hex(self.result[21:23]), 16) #in mV
        self.cell4_voltage = int(binascii.b2a_hex(self.result[23:25]), 16) #in mV
        self.cell5_voltage = int(binascii.b2a_hex(self.result[25:27]), 16) #in mV
        self.cell6_voltage = int(binascii.b2a_hex(self.result[27:29]), 16) #in mV
        
        #print 'unknown2: ', binascii.b2a_hex(self.result[29:])

        if self.header_byte != '0f':
            print colored('Header not correct! Aborting decoding. Received: ' + self.header_byte, 'red')
            return False

        if self.packet_lenth != '22':
            print colored('Unexpected packet length! Aborting decoding. Received: ' + self.packet_lenth, 'red')
            return False

        if self.transaction_type != '55':
            print colored('Wrong transaction type! Aborting decoding. Received: ' + self.transaction_type, 'red')
            return False

        if self.unknown1 != '00':
            print colored('!!! Values changed !!! previous: 00', 'red')


        if binascii.b2a_hex(self.result[36:38]) != 'ffff':
            print colored('Stop sign not correct! Aborting decoding. Received: ' + binascii.b2a_hex(self.result[39:41]), 'red')
            return False

        return True
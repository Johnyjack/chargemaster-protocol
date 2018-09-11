import usb1
import binascii
import sys
#from analyzeReply import *
from battery_class import *


VENDOR_ID = 0000
PRODUCT_ID = 0001
INTERFACE = 0
context = usb1.USBContext()

result = context.getDeviceList(skip_on_access_error=False, skip_on_error=False)

deviceList = []

for device in result:
    if device.getVendorID() == VENDOR_ID and \
                    device.getProductID() == PRODUCT_ID:
        print('found')
        busnum = device.getBusNumber()
        print 'Bus Nr.:', busnum
        portlist = device.getPortNumberList()
        print 'Port list:', portlist
        address = device.getDeviceAddress()
        print 'Device bus address:', address
        deviceList.append(device)

if len(deviceList) < 1:
    print 'error: no device found'
else:
    device = deviceList[0]
    usb_handle = device.open()

    if usb_handle.kernelDriverActive(INTERFACE):
        print('kernel active')
        usb_handle.detachKernelDriver(INTERFACE)
        print('kernel detached')
        if usb_handle.kernelDriverActive(INTERFACE):
            print('error detaching kernel')
    else:
        print('kernel inactive')

    usb_handle.claimInterface(INTERFACE)
    print 'interface claimed'

#----debugging----#
# command = '55'
# result = get_response(command, usb_handle)
# print 'response: ', binascii.b2a_hex(result)
# transaction_55(result)

#A test should run as follows...
#setup action (charge or discharge) manually
#start script
#start the action manually
#the script will then log the data in csv format to a file based on the date and stop logging when the action ends

#things necessary in the battery class:
#check if action is_running: --> from trans55
#if yes, pull voltage data and current data
#battery class init (battery_chem, series_cells, batt_capacity, usb_device_handle, log_filename)
graphene_4s = BatteryClass('lipo', 4, 1000, usb_handle, 'test_data1')
graphene_4s.is_logging = True
graphene_4s.get_data()
graphene_4s.log_data_header()

while (graphene_4s.action_state == 1):
    graphene_4s.get_data()
    graphene_4s.log_data()
    time.sleep(1)
graphene_4s.get_data()
graphene_4s.log_data()


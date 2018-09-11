import usb1
import binascii
from analyzeReply import *
from battery_class import battery_class


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
    handle = device.open()

    if handle.kernelDriverActive(INTERFACE):
        print('kernel active')
        handle.detachKernelDriver(INTERFACE)
        print('kernel detached')
        if handle.kernelDriverActive(INTERFACE):
            print('error detaching kernel')
    else:
        print('kernel inactive')

    handle.claimInterface(INTERFACE)
    print 'interface claimed'

#----debugging----#
# command = '55'
# result = get_response(command, handle)
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
graphene_4s = battery_class('lipo', 4, 4400) #unsure if capcity is correct
graphene_4s.is_logging = True
while (graphene_4s.start_logging)
    if graphene_4s.get_data()
        graphene_4s.log_data()
    if graphene_4s.is_running_action == False
        graphene_4s.is_logging == False
graphene_4s.get_data()
graphene_4s.log_data()


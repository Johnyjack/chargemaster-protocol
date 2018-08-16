import usb1
import binascii
from analyzeReply import *


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

command = '55'
result = get_response(command, handle)
print 'response: ', binascii.b2a_hex(result)
transaction_55(result)
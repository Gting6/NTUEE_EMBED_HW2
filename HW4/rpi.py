from bluepy.btle import Peripheral, UUID
from bluepy.btle import Scanner, DefaultDelegate
import struct


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", dev.addr)
        elif isNewData:
            print("Received new data from", dev.addr)


class MyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        # ... initialise here

    def handleNotification(self, cHandle, data):
        # ... perhaps check cHandle
        # ... process 'data'
        print(f'notified data: {data.hex()}')
        # print("hello 123")
        return


scanner = Scanner()
print("Scanning for 5 seconds...")
devices = list(scanner.scan(5.0))
for i, dev in enumerate(devices):
    print("#%d: %s (%s), RSSI=%d dB" % (i, dev.addr, dev.addrType, dev.rssi))
    for (adtype, desc, value) in dev.getScanData():
        if desc == "Complete Local Name":
            print("  %s = %s" % (desc, value))

print()
number = int(input('Enter your device number: '))
print(f'Connecting to #{number}: {devices[number].addr}')

dev = Peripheral(devices[number].addr, devices[number].addrType)
dev.setDelegate(MyDelegate())

services = dev.getServices()

print()
print("Available Services:")
for svc in services:
    print("Service", str(svc.uuid), svc)

try:
    target_svc = input("service uuid: ")
    print(target_svc)
    testService = dev.getServiceByUUID(target_svc)
    print()
    print("Available Characteristics:")
    for ch in testService.getCharacteristics():
        print(ch.uuid, str(ch))
    target_char = input("char uuid: ")
    ch = dev.getCharacteristics(uuid=UUID(target_char))[0]
    ch_handle = ch.getHandle()
    ch_notify_handle = ch_handle + 1

    while True:
        dev.writeCharacteristic(
            ch_notify_handle, struct.pack('<bb', 0x01, 0x00))
        dev.waitForNotifications(10)

finally:
    dev.disconnect()

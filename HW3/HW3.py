from bluepy.btle import Peripheral, UUID
from bluepy.btle import Scanner, DefaultDelegate
from pprint import pprint
import struct
import time


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
        print(f'notified data: {data.decode("utf-8")}')
        # print("hello 123")
        return


scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(5.0)  # scan period
devices = list(devices)
n = 0
for dev in devices:
    print("%d: Device %s (%s), RSSI=%d dB" %
          (n, dev.addr, dev.addrType, dev.rssi))
    n += 1
    for (adtype, desc, value) in dev.getScanData():
        print(" %s = %s" % (desc, value))

number = int(input('Enter your device number: '))
print('Device', number)
# print(devices[number].addr)
# print(devices)

print("Connecting...")
dev = Peripheral(devices[number].addr, 'random')
print("Connected")

dev.setDelegate(MyDelegate())

print("Services...")
for svc in dev.services:
    print(str(svc))

while True:

    operation = input('operation?')
    print(operation)

    if operation == "finish":
        break

    elif operation == "chars":
        try:
            testService = dev.getServiceByUUID(UUID(0xfff0))
            for ch in testService.getCharacteristics():
                print(str(ch))

        except:
            print("error")

    elif operation == "read":
        try:
            testService = dev.getServiceByUUID(UUID(0xfff0))
            for ch in testService.getCharacteristics():
                print(str(ch))
            char = input("which char?(EX:fff1)")
            char = int(char, 16)

            ch = dev.getCharacteristics(uuid=UUID(char))[0]
            if (ch.supportsRead()):
                print(ch.read())

        except:
            print("error")

    elif operation == "write":
        try:
            testService = dev.getServiceByUUID(UUID(0xfff0))
            for ch in testService.getCharacteristics():
                print(str(ch))
            char = input("which char?(EX:fff1)")
            char = int(char, 16)
            msg = input("input message")

            ch = dev.getCharacteristics(uuid=UUID(char))[0]
            ch_handle = ch.getHandle()
            dev.writeCharacteristic(ch_handle, msg)
            print("writing")
            dev.waitForNotifications(10)

        except:
            print("error")

    elif operation == "cccd":
        try:
            testService = dev.getServiceByUUID(UUID(0xfff0))
            for ch in testService.getCharacteristics():
                print(str(ch))

            char = input("which char?(EX:fff1)")
            char = int(char, 16)

            op = input("notify/indicate/disable")

            ch = dev.getCharacteristics(uuid=UUID(char))[0]
            ch_handle = ch.getHandle()
            ch_notify_handle = ch_handle + 2

            if op == "notify":
                print("Enable Notify")
                dev.writeCharacteristic(
                    ch_notify_handle, struct.pack('<bb', 0x01, 0x00))
                dev.waitForNotifications(10)

            elif op == "indicate":
                print("Enable Indicate")
                dev.writeCharacteristic(
                    ch_notify_handle, struct.pack('<bb', 0x02, 0x00))
                dev.waitForNotifications(10)

            elif op == "disable":
                print("Disable All")
                dev.writeCharacteristic(
                    ch_notify_handle, struct.pack('<bb', 0x00, 0x00))
                time.sleep(3)

            else:
                print("cccd error")

        except:
            print("error")
    else:
        print("chars/read/write/cccd/finish")

    print("done")

dev.disconnect()

import serial
import time

# On macos, use the "ls /dev/tty.*" command in the Terminal to get the list of every available serial ports.
arduSer = serial.Serial('/dev/tty.usbserial', 9600, timeout=2)
arduSer.close()

# %%

arduSer.open()
time.sleep(1)
arduSer.write(10)
if int(arduSer.readline()) == 1:
    print('Command Recieved!')
while int(arduSer.readline()) != 2;
print('Rotation Done!')
arduSer.close()

#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------
# This python code is 

import io
import fcntl
import struct
import time
import smbus

I2C_SLAVE=0x0703

#uncomment one line below for the sensor type used (Pi16340 SMART UPS uses Digital Sensor)
#SENSOR_HUMIDITY = "Analog"
SENSOR_HUMIDITY = "Digital"

class i2c:

   def __init__(self, device, bus):

      self.fr = io.open("/dev/i2c-"+str(bus), "rb", buffering=0)
      self.fw = io.open("/dev/i2c-"+str(bus), "wb", buffering=0)

      # set device address

      fcntl.ioctl(self.fr, I2C_SLAVE, device)
      fcntl.ioctl(self.fw, I2C_SLAVE, device)

   def write(self, data):
      if type(data) is list:
            data = bytes(data)
      self.fw.write(data)

   def read(self, bytes):
      return self.fr.read(bytes)

   def close(self):
      self.fw.close()
      self.fr.close()

   def get_int(self, var_slice):
       
      ms = memoryview(var_slice)
      var_list = map(ord,ms)
      #print("bat_list: ", bat_list)
      var_int = var_list[0]*256 + var_list[1]

      return var_int

   def get_single_int(self, var_slice):
       
      ms = memoryview(var_slice)
      var_list = map(ord,ms)
      #print("bat_list: ", bat_list)
      var_int = var_list[0]
      
      return var_int





#<<----------------------------------------------------------------------------------------
#comment out this section below if you would like to import the class into your own program
#---------------------------------------------------------------------------------------->>
testpoll = i2c(0x48,1)
samples = 5
bat_avg = 0
hum_avg = 0
temp_avg = 0
sample_delay = 0.010

for i in range(samples):
      result = testpoll.read(10)
      print("result: ", result)

      bat = result[:2]
      hum = result[2:4]
      temp = result[4:6]
      mode = result[6:7]
      reboot = result[7:8]
      pwrlvl = result[8:9]
      temp2 = result[-1:]

      #print("bat: ", bat)
      #print("hum: ", hum)
      #print("temp: ", temp)


      for j in range(6):
          if j == 0:
             res = testpoll.get_int(bat)
             bat_avg = bat_avg + res

          elif j == 1:
             res1 = testpoll.get_int(hum)
             hum_avg  = hum_avg + res1

          elif j == 2:
             res2 = testpoll.get_int(temp)
             temp_avg  = temp_avg + res2

          elif j == 3:
             mode_res = testpoll.get_single_int(mode)

          elif j == 4:
             reboot_res = testpoll.get_single_int(reboot)

          elif j == 5:
             pwrlvl_res = testpoll.get_single_int(pwrlvl)
          else:
             no_op = ""




      result = '0'
      res = 0
      res1 = 0
      res2 = 0
      time.sleep(sample_delay)



#m = memoryview(bat)
#bat_list = map(ord,m)
#print("bat_list: ", bat_list)

#Battery Level calculation---------------
#bat_int = bat_list[0]*256 + bat_list[1]
#print("bat_int: ", bat_int)

bat_avg_int = bat_avg / samples
battery = (float(bat_avg_int) * 0.00322) / 0.7674
print "Battery: ", battery ,"V"


#----------------------------------------


if SENSOR_HUMIDITY == "Analog":

    #Analog sensor is read directly from the MSP439 MCU and reported back to the Pi once querried via I2C
 

    #m1 = memoryview(hum)
    #hum_list = map(ord,m1)
    #print("hum_list: ", hum_list)

    #Humidity calculation--------------------
    #hum_int = hum_list[0]*256 + hum_list[1]
    #print("hum_int: ", hum_int)

    humidity = 0.0
    hum_avg_int = hum_avg / samples
    humidity = float(-12.5) + (float(125) * (float(hum_avg_int) / float(1024)))
    humidity  = round(humidity,2)
    print "Humidity: ", humidity ,"%"
    #----------------------------------------

    #m2 = memoryview(temp)
    #temp_list = map(ord,m2)
    #print("temp_list: ", temp_list)

    #Temperature calculation - Deg C-----------
    #temp_int = temp_list[0]*256 + temp_list[1]
    #print("temp_int: ", temp_int)

    temperature = 0.0
    temp_avg_int = temp_avg / samples
    temperature = float(-66.875) + (float(218.75) * (float(temp_avg_int) / float(1024)))
    temperature = round(temperature,2)
    print "Temperature: ", temperature ,"C"
    #-----------------------------------------

    #Temperature calculation - Deg F-----------
    #temp_int = temp_list[0]*256 + temp_list[1]
    #print("temp_int: ", temp_int)

    temperatureF = 0.0
    temp_avg_int = temp_avg / samples
    temperatureF = float(-88.375) + (float(393.75) * (float(temp_avg_int) / float(1024)))
    temperatureF = round(temperatureF,2)
    print"Temperature: ", temperatureF ,"F"
    #-----------------------------------------

    #mode = mode.strip()
    #reboot = reboot.strip()
    #mode = mode.replace('\\', ' ')
    #reboot = reboot.replace('\\', ' ')



if mode_res == 0:
      print"Mode: Battery(", mode_res, ")"
else:
      print"Mode: UPS(", mode_res, ")"

reboot_res = reboot_res >> 4
print"Reboot Status: ", reboot_res

pwrlvl_res = pwrlvl_res >> 5
print"Supply Power Level Status: ", pwrlvl_res


#dev.write("\x2D\x00") # POWER_CTL reset

testpoll.close()




#Read the temperature-humidity sensor using the smbus module-----------------------#



#select the bus used in communications, usually 1 but could be zero, this can be checked using the i2cdetect -y 1 or 0 command
i2cbus = smbus.SMBus(1)

#address of sensor configured as 0x44
th_address = 0x44
startReg = 0x00

#now send the measurement command with high accuracy
i2cbus.write_i2c_block_data(th_address, 0x2C, [0x06])

#we need to give a short delay for the measurements to be taken
time.sleep(0.5)


#according to the data sheet the measurement for each temperature and humidity are followed by a CRC byte
# tempHi, tempLo, tempCRC, humHi, humLo, humCRC 
#so 6 bytes in total will be read
sensorBytes = bus.read_i2c_block_data(th_address, startReg, 0x06)

#convert the data to a readable format
TemperatureWord = (sensorBytes[0] * 256.0) + sensorBytes[1]) 
TemperatureC = ((TemperatureWord * 175.0) / 65535.0) - 45
TemperatureF = (TemperatureC * 1.8) + 32

humidityWord = (sensorBytes[3] * 256 + sensorBytes[4]) 
HumidityVal = (humidityWord * 100.0) / 65535.0


print("Temperature:  %.2F C", cTemperatureVal)
print("Temperature:  %.2F F", fTemperatureVal)
print("HumidityVal: %.2F RH", HumidityVal)

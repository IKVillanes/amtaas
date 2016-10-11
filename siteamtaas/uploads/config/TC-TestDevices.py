#!/usr/bin/python

#from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
#import os, threading, glob, subprocess
#from datetime import datetime
import sys
import time
import subprocess
import glob
import defPath #File with path of directoeries

##
# Function readlistavds:
#   Open and read files with name of emulators from
#   server and from users selected
# @server_devices = file'name that have all emulators on server
# @user_devices = file's name with device's name that users selected
def main():
   server_devices = sys.argv[1] #  print server_devices
   user_devices = sys.argv[2]   #  print user_devices
   # Path User Script and APK
   user_path_apk = sys.argv[3]  # print user_path_apk
   user_path_script = sys.argv[4] # print user_path_script
   user_id = sys.argv[5] # print user_id
   user_log_path = defPath.src_rootFolder + user_id + defPath.src_log




   #Path Directories
#   path_monkeyrunner = "/home/experts/android-sdk-linux/tools/"
#   path_scriptTest = "/var/www/html/siteamtaas/uploads/script_files/TC-TestExeOTA1.py"
   path_monkeyrunner = defPath.sdk_tools 
   print path_monkeyrunner
   path_scriptTest = defPath.scriptOTA
   print path_scriptTest
   


   file = open(server_devices,'r')
   emulist = file.readlines()
   emuonline = [] #List with devices in server [['<nameAVD>', 'emulator-<ID>'], ['<nameAVD>', 'emulator-<ID>']]
   n=0
   for i in range(len(emulist)):
    emuonline.append(emulist[i].rstrip('\n').split(','))
   file.close()

   udev = open(user_devices,'r')
   udevlist = udev.readlines()
   udevlisttotest = [] #List with devices that users selected [['<nameAVD>], ['<nameAVD>']]
   for j in range(len(udevlist)):
    udevlisttotest.append(udevlist[j].rstrip('\n'))
   udev.close()

#Verify if devices selected by user are in available Emulator_List_Online
   listdevtotest = [] #Final list with devices that will be used for test
   for userdevice in udevlisttotest:
     for index, line in enumerate(emuonline):
       if userdevice in emuonline[index]:
         print userdevice, emuonline[index]
         listdevtotest.append(emuonline[index])
         break

   print "devices to test"
   print (listdevtotest)
   if (user_path_script!="none"):
      user_path_script+='*.py' #All files with .py extension
   

#For each device execute Test OTA
   for index, line in enumerate(listdevtotest):
     emulatorid = listdevtotest[index][0]
     deviceid = listdevtotest[index][1]
     print emulatorid #    result = C-GA-avd18xxxx...
     print deviceid   #    result = emulator-xxxx
     subprocess.call(path_monkeyrunner + 'monkeyrunner -v ALL ' + path_scriptTest + ' ' + deviceid + ' ' + emulatorid + ' ' + str(index) + ' ' + user_id, shell=True)
     time.sleep(10)

     if (user_path_script!="none"):
        for file in sorted(glob.glob(user_path_script)):
            #subprocess.call('python ' + user_path_script + ' ' + deviceid + ' ' +  emulatorid, shell=True)
            subprocess.call('python ' + file + ' ' + deviceid + ' ' +  emulatorid + ' ' + user_log_path, shell=True)
        print user_path_script
     else:
        print "none user script"
     
   print "___END___"

if __name__ == "__main__":
    main()

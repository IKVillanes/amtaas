from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
import os, threading, glob, subprocess
from datetime import datetime
import sys
import re
import defPath #File with path of directoeries 
startTime1 = datetime.now()

##
# Function: main
#   Open and read files with name of emulators from
#   server and from users selected
# @emulatorid = receive emulator's name
# @deviceid = receive internal name of emulated devices online
# @count = receive number(index) of emulators
def main():
   print "_____   [Starting Devices]   _____"
   deviceid = sys.argv[1]
   print "[Emulator Internal Name] %s" % deviceid
   emulatorid = sys.argv[2]
   print "         [Emulator Name] %s" % emulatorid
   count = sys.argv[3]

   device = MonkeyRunner.waitForConnection('',deviceid)
   droidTesting = DefaultDroidTest(device, count, emulatorid, deviceid)
   droidTesting.run()

#
# Funcion: get_package_activity_name(apk_address)
#
def get_package_activity_name(apk_address):
#    command = "/home/experts/android-sdk-linux/platform-tools/aapt dump badging %s" %apk_address
    command = defPath.sdk_plaTool +  "aapt dump badging %s" %apk_address
    aapt_result = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]
    lines = aapt_result.split("\n")
    myDic = {}
    for line in lines:
        splitedline=line.split(":")
        if len(splitedline)==2:
            myKey,myValue=line.split(":")
            myDic[myKey]=myValue
    package = myDic['package'].split("'")[1]
    activity = myDic['launchable-activity'].split("'")[1]
#    activity = myDic['launchable-activity'].split("'")[1].split(".")[-1]
    return package, activity

def saveresult(fr, device, msg):
    f_result = open(fr, 'wt')
    if msg is None:
        msg = 'None'
    f_result.write(msg.encode('utf-8'))
    f_result.close()

def log(fn, device):
    msg = device.shell('logcat -d')
    f_log = open(fn, 'at')
    if msg is None:
        msg = 'None'
    f_log.write(msg.encode('utf-8'))
    f_log.close()
    device.shell('logcat -c')

##
# Function: eraseLog(device)
# Clean Emulator(device)'s log
def eraseLog(device):
    device.shell('logcat -c')

##
# verify_package_in_avd(device) whit enought memory
# List all external packages installed on device(emulator) 
def verify_package_in_avd(device,packagename):
    command = device.shell("pm list packages -3")
    splitedline=re.split(':|\r|\n',command)
    if any(packagename in s for s in splitedline):
       msg = "failed,"
    else:
       msg = "passed,"
    return msg

##
# verify_package_in_avd(device) Normal Memory
# List all external packages installed on device(emulator) 
def verify_package_in_normal_avd(device,packagename):
    command = device.shell("pm list packages -3")
    splitedline=re.split(':|\r|\n',command)
    if any(packagename in s for s in splitedline):
       msg = "passed,"
    else:
       msg = "failed,"
    return msg

#
#
def check_free_space(device):
    r = device.shell("df|grep data")
    pos = r.rfind("M")
    s = r[pos-6:pos].strip()
    mf = int(float(s))
    return mf

def shutdown_avd(deviceid):
    #command = "/home/experts/android-sdk-linux/platform-tools/adb -s " + deviceid + " emu kill"
    command = defPath.sdk_plaTool + "adb -s " + deviceid + " emu kill"
    subprocess.call(command, shell=True)

def uninstall_apk(device,packagename):
    print "Starting App Uninstaller... "
    device.shell ("pm uninstall " +  packagename)

#sf: size file of free memory available
def select_files(fmemsize):
    lsf = {}
    fms= int(fmemsize)
    if fms>0:
      for p in 100, 50, 20, 10, 5, 2, 1:
         if fms >= p:
            n = fms/p
            r = fms-p*n
            lsf[p]=n
            fms = r
    else:
      return (lsf)
    return (lsf)


def copy_files(lsf,device,deviceid):
    #src_path = '/var/www/html/siteamtaas/uploads/script_files/filesmb/'
    src_path = defPath.src_filesmb
    dst_path = " /data/"
#    print "------lista files-----"
#    print lsf
    for v, q in lsf.items():
      src = 'filetxt' + str(v) + 'mb.txt'
      x=1
      while x <= q:
       dstfile = src_path + str(x) + src
#       print 'copiando ' + str(dstfile) 
#       command = "/home/experts/android-sdk-linux/platform-tools/adb -s "+ deviceid + " push " + dstfile + " /data/"
#       command = "/home/experts/android-sdk-linux/platform-tools/adb -s "+ deviceid + " push " + dstfile + dst_path
       command = defPath.sdk_plaTool + "adb -s "+ deviceid + " push " + dstfile + dst_path

       subprocess.call(command, shell=True)
       x+=1
      src = ""

def list_files_del(device):
    command = device.shell("ls /data/ | grep filetxt")
    splitedline=re.split('\r|\n',command)

    for filetxt in splitedline:
       res=device.shell("rm -f /data/"+filetxt)

class DefaultDroidTest:
    deviceid = sys.argv[1]
    emulatorid = sys.argv[2]
    usr_id = sys.argv[4]

#    sdktoolfolder = '/home/experts/android-sdk-linux/platform-tools'
#    rootfolder = '/var/www/html/siteamtaas/uploads/'

    #apkfolder = rootfolder + 'app_files/'
    apkfolder = defPath.src_rootFolder + usr_id + defPath.src_app_files

    imagefolder = defPath.src_rootFolder + usr_id + defPath.src_img

    #logfolder = rootfolder + 'log/'
    logfolder = defPath.src_rootFolder + usr_id + defPath.src_log

    #resfolder = rootfolder + 'log/' + emulatorid + '/'
    resfolder = defPath.src_rootFolder + usr_id + defPath.src_log + emulatorid + '/'

#    startTime1 = datetime.now()

    if not os.path.exists(resfolder):
        os.makedirs(resfolder)

    def __init__(self, device, count, emulatorid, deviceid):
        self.device = device
        self.count = count
        self.emulatorid = emulatorid
        self.deviceid = deviceid

    def run(self):
        eraseLog(self.device)
        fs_1 = check_free_space(self.device)
        
        for apk in glob.glob(self.apkfolder + '/*.apk'):
            print "Getting package and activity name..."
            packagename,activity = get_package_activity_name(apk)
            componentname = packagename + "/." + activity

            apk_path = self.device.shell('pm path ' + packagename)
            print "inicio"
            print apk_path
            print "fim"
            if not apk_path:
               print "Installing " + str(packagename) + " ..."
               result_install = self.device.installPackage(apk)
               
            else:
               if apk_path.startswith('package:'):
                  print "Apk has already installed, re-installing..."
                  result_install = self.device.installPackage(apk)
               #Adicionado por WARNING do API19
               else:
                  if apk_path.startswith('WARNING:'):
                     print "Apk has already installed, re-installing..."
                     result_install = self.device.installPackage(apk)

        #vrik: verifica se package esta no dispositivo    
        print "Verifying if Apk was installed"
        if (result_install):
           print "*****NEW**** Apk installed successfully"
           msg = "passed,Installation,"
        else:
           print "*****NEW**** Apk NOT installed"
           msg = "failed,Installation,"
        fs_2 = check_free_space(self.device)
     
        time1 = datetime.now() - startTime1
        msg+=str(time1)

        print "Saving results..."
        saveresult(self.resfolder + self.emulatorid + 'ota1' + '.txt',self.device, msg)
        msg=""

        startTime2 = datetime.now()
        MonkeyRunner.sleep(10)

#Uninstall APK
        print "Uninstalling...."
        print packagename
        print activity
        print componentname
        uninstall_apk(self.device,packagename)

#vrik: verifica se package esta no dispositivo
        print "Verifying if Apk was uninstalled"
        msg = verify_package_in_avd(self.device,packagename)
        msg+= "Uninstall,"
#        ListPackageToSearch = search_package_in_avd(self.device)

#        if any(packagename in s for s in ListPackageToSearch):
#            msg = "Uninstall,failed,"
#        else:
#            msg = "Uninstall,passed,"

        time2 = datetime.now() - startTime2
        msg+=str(time2)

        print "Saving results..."
        saveresult(self.resfolder + self.emulatorid + 'ota2' + '.txt',self.device, msg)

        startTime3 = datetime.now()
        fs_3 = (fs_1 - fs_2)
        fs_4 = check_free_space(self.device)
        free_mem = fs_4 - (fs_3 - 1)

#Copy files based on free memory size
        print "Filing memory..."
        lf = select_files(free_mem)
        copy_files(lf,self.device,self.deviceid)

#TC-memory test - install
        print "Installing Apk without enought memory..."
        for apk in glob.glob(self.apkfolder + '/*.apk'):
            self.device.installPackage(apk)

#Verify if Package is on device
        print "Verifying if Apk was installed"
        msg = verify_package_in_avd(self.device,packagename)
        msg+= "No space left on device,"

#        ListPackageToSearch = search_package_in_avd(self.device)

#        if any(packagename in s for s in ListPackageToSearch):
#            print "Warning - Apk installed with few memory"
#            msg = "No space left on device,failed,"
#        else:
#            print "Apk was not installed - No space left on device"
#            msg = "No space left on device,passed,"

        time3 = datetime.now() - startTime3
        msg+=str(time3)

        print "Saving results..."
        saveresult(self.resfolder + self.emulatorid + 'ota3' + '.txt',self.device, msg)

        print "Freeing up memory space"
        list_files_del(self.device)


# Install App for User Test
        print "Installing Apk for User Test..."
        for apk in glob.glob(self.apkfolder + '/*.apk'):
            self.device.installPackage(apk)

        res = verify_package_in_normal_avd(self.device,packagename)
        print res

        #image = self.device.takeSnapshot()
        #image.writeToFile(self.imagefolder + 'screenshot_' + packagename + str(self.count) + '.png','png')
        #log(self.logfolder + 'test' + str(self.count) +'.log', self.device);
        log(self.resfolder + self.emulatorid + 'logtest' +'.log', self.device);


        #print 'Execution Time', datetime.now() - startTime
        
#        shutdown_avd(self.deviceid)
        print "__________ FINISHED ___________"
if __name__ == "__main__":
    main()

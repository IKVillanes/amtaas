#!/bin/bash

## Port number to start searching for free ports for the console
# CONSOLE_PORT needs to be an even integer and can only be within a range of 5554-5584.
if [ "x${console_port_start}" != "x" ]; then
    console_port="${console_port_start}"
else
    console_port="5554"
fi

# readlistavds: Function that read file that have a list of name of emulators
function readlistavds {
   local name_file=$1
   n=0
   while read line
   do
      list_avd[n]=$line
      #echo ${list_avd[$n]}
      n=$(( $n + 1 ))
   done < "$name_file"
      #echo ${list_avd[@]}
      #echo "numero de emuladores " ${#list_avd[@]}

  # Variables
  ## Define how many emulators will be created
  if [ "x${emulator_count}" != "x" ]; then
      EMULATOR_COUNT="${emulator_count}"
  else
      EMULATOR_COUNT="${#list_avd[@]}"
  fi
}

## Funtions

# findFreePorts: Create an array of free port numbers to use for the emulators
# $ports[]: array with free ports to use
function findFreePorts {
	k=0
	for (( i=0 ; i < $EMULATOR_COUNT; i++ ))
	{
		while netstat -atwn | grep "^.*${console_port}.*:\*\s*LISTEN\s*$"
		do
			#Console Port should and can only be an even number
			#Android allows only even numbers
			console_port=$(( ${console_port} + 2 ))
			echo PORT1 ${console_port}
		done

		ports[$k]=${console_port}
		k=$(( $k + 1 ))

		#Android allows only even numbers
		console_port=$(( ${console_port} + 2 ))
	}
}

# startEmulator: Start the emulate AVDs and call to function wait_for_boot_complete
# $CONSOLE_PORT: parameter receives the number of free port
# $AVD_NAME: parameter receives o nome do emulador AVD
# $file_name: File to save all AVDs in listavds.txt pattern: nome-emulator, nome-device
function startEmulator {
  local CONSOLE_PORT=$1
  local AVD_NAME=$2
  local FILE_NAME=$3
   echo "Starting emulator with avd"
#   echo "variaveis 3 $FILE_NAME
   echo "$AVD_NAME,emulator-$CONSOLE_PORT" >> ${FILE_NAME}
   emulator -avd $AVD_NAME -port $CONSOLE_PORT -wipe-data -noaudio &

   # This waits for emulator to start up
   echo  "[emulator - $AVD_NAME] Waiting for emulator to boot completely"
   wait_for_boot_complete "getprop dev.bootcomplete" 1
   wait_for_boot_complete "getprop sys.boot_completed" 1
   wait_for_boot_complete "pm path android" package
}

# wait_for_boot_complete: Function to wait until device emulator is ready to use 
# boot_property: receive the property's name
# boot_property_test: receive the expected result from property´s name
function wait_for_boot_complete {
   local boot_property=$1
   local boot_property_test=$2
   echo "[emulator-$CONSOLE_PORT $AVD_NAME] Checking $boot_property..."
   local result=`adb -s emulator-$CONSOLE_PORT shell $boot_property | grep "$boot_property_test"`
   while [ -z $result ]; do
      sleep 1
      result=`adb -s emulator-$CONSOLE_PORT shell $boot_property | grep "$boot_property_test"`
      echo "result ->" $result
   done
   echo "[emulator-$CONSOLE_PORT] All boot properties succesful"
}

# main: Function main to start
# $1 file_name of emulators to start
# $2 file_nme where list of emulator will be save
function main {
  # Function to Get name of emulators
  readlistavds $1

  # Get name of file to save list AVDs and delete old content
  local file_name_txt=$2
  truncate -s 0 $file_name_txt
  # Function to Get an array of free port numbers to use
  findFreePorts

  ## now loop through the above array in ports
  e=0
  for i in "${ports[@]}"
  do
    echo "Porto " $i
    echo "Emulator " ${list_avd[$e]}
    #CONSOLE_PORT  e  NAME_AVD
    startEmulator $i ${list_avd[$e]} $file_name_txt
    e=$(($e+1))
  done

  echo "Starting Emulator - Finished"
}

## Execute the script
main $1 $2

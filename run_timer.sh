#!/bin/bash
source .env

LOGDIR="/home/thomas/DerbyNet/timerlogs"
SERVER_URL="https://derbynet.buetowfamily.net/"
USERNAME="Timer"
LANES="4"
DEVICE="NewBold"

#Race timer arguments
#java -jar /home/thomas/DerbyNet/derby-timer.jar -logdir $LOGDIR -x -u $USERNAME -p $PASSWORD -d $DEVICE $SERVER_URL

#Specify lanes
#java -jar /home/thomas/DerbyNet/derby-timer.jar -logdir $LOGDIR -x -u $USERNAME -p $PASSWORD -d $DEVICE -lanes $LANES $SERVER_URL

#Simulate timer
java -jar /home/thomas/DerbyNet/derby-timer.jar -logdir $LOGDIR -x -u $USERNAME -p $PASSWORD -d $DEVICE -simulate-timer $SERVER_URL

import socket
import webiopi
import sys, codecs
import re

webiopi.setDebug()

GPIO = webiopi.GPIO

PIN_L1 = 23
PIN_L2 = 24
PIN_R1 = 11
PIN_R2 = 9

g_mode = 0
g_percentage = 50
count_w = 0
GPIO.setFunction( PIN_L1, GPIO.PWM )
GPIO.setFunction( PIN_L2, GPIO.PWM )
GPIO.setFunction( PIN_R1, GPIO.PWM )
GPIO.setFunction( PIN_R2, GPIO.PWM )

def MotorDrive( iIn1Pin, iIn2Pin, percentage ):
	if 100 < percentage:
		percentage = 100
	if -100 > percentage:
		percentage = -100
	if 10 > percentage and -10 < percentage:
		GPIO.pwmWrite( iIn1Pin, 0.0 )
		GPIO.pwmWrite( iIn2Pin, 0.0 )
	elif 0 < percentage:
		GPIO.pwmWrite( iIn1Pin, percentage * 0.01 )
		GPIO.pwmWrite( iIn2Pin, 0.0 )
	else:
		GPIO.pwmWrite( iIn1Pin, 0.0 )
		GPIO.pwmWrite( iIn2Pin, -percentage * 0.01 )

@webiopi.macro
def ChangeDriveMode( mode ):
	if mode == "0":
		webiopi.debug("ChangeDriveMode : Stop")
		MotorDrive( PIN_L1, PIN_L2, 0 );
		MotorDrive( PIN_R1, PIN_R2, 0 );
	elif mode == "1":
		webiopi.debug("ChangeDriveMode : Forward")
		MotorDrive( PIN_L1, PIN_L2, g_percentage );
		MotorDrive( PIN_R1, PIN_R2, g_percentage );
	elif mode == "2":
		webiopi.debug("ChangeDriveMode : Backward")
		MotorDrive( PIN_L1, PIN_L2, -g_percentage );
		MotorDrive( PIN_R1, PIN_R2, -g_percentage );
	elif mode == "3":
		webiopi.debug("ChangeDriveMode : CW")
		MotorDrive( PIN_L1, PIN_L2, g_percentage );
		MotorDrive( PIN_R1, PIN_R2, -g_percentage );
	elif mode == "4":
		webiopi.debug("ChangeDriveMode : CCW")
		MotorDrive( PIN_L1, PIN_L2, -g_percentage );
		MotorDrive( PIN_R1, PIN_R2, g_percentage );
	global g_mode
	g_mode = mode


@webiopi.macro
def ChangeVoltageLevel( level ):
	webiopi.debug("ChangeVoltageLevel : %s" % (level))
	global g_percentage
	g_percentage = 10 * int(level)
	ChangeDriveMode( g_mode )

MotorDrive( PIN_L1, PIN_L2, 50 );
MotorDrive( PIN_R1, PIN_R2, 50 );
webiopi.sleep( 1.0 )
MotorDrive( PIN_L1, PIN_L2, 0 );
MotorDrive( PIN_R1, PIN_R2, 0 );



pat = re.compile("(((left)|(right))\\s*,\\s*(\\d+))")
patw = re.compile("((w)|(W))")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.11.12', 8092))
while 1:
    data = client_socket.recv(512)
    if data:
        for m in pat.findall(data.decode("shift-jis")):
            print m[1] + " | " + m[4]
            if int(m[4]) < 0:
                motor = 0
            elif int(m[4]) > 100:
                motor = 100
            else:
                motor = int(m[4]) 
            if m[1]=="left":
            	MotorDrive( PIN_L1, PIN_L2, g_percentage );
            	MotorDrive( PIN_R1, PIN_R2, -g_percentage );
            	webiopi.sleep( 1.0 )
            	MotorDrive( PIN_L1, PIN_L2, 0 );
            	MotorDrive( PIN_R1, PIN_R2, 0 );
            if m[1]=="right":
            	MotorDrive( PIN_L1, PIN_L2, -g_percentage );
            	MotorDrive( PIN_R1, PIN_R2, g_percentage );
            	webiopi.sleep( 1.0 )
            	MotorDrive( PIN_L1, PIN_L2, 0 );
            	MotorDrive( PIN_R1, PIN_R2, 0 );

            #otorDrive( IN1PIN, IN2PIN, motor )

        r = re.compile(r">(.+?)<\/chat")
        returnlist = r.findall(data.decode("shift-jis"))

        if returnlist:
            print returnlist[0].encode('utf-8')
            for m in patw.findall(returnlist[0]):
                count_w+= 1
        if count_w > 0:
       		MotorDrive( PIN_L1, PIN_L2, 50 );
        	MotorDrive( PIN_R1, PIN_R2, 50 );
        	webiopi.sleep( 1.0 )
       		MotorDrive( PIN_L1, PIN_L2, 0 );
        	MotorDrive( PIN_R1, PIN_R2, 0 );
        	count_w=0
        print "w_count:", count_w
        
    client_socket.send(data)
    data = ""
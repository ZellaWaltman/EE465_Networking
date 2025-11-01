#!/usr/bin/env python3

import RPi.GPIO as GPIO
import subprocess, time, sys

# LCD MAPPING
D7 = 18
D6 = 23
D5 = 24
D4 = 25
E  = 27
RS = 22

# Button - 10k Pull Down Resistor, 3.3 V supply
BTN = 17

# Define LCD constants
LCD_Width = 16 # Max characters
LCD_chr = True
LCD_cmd = False

LCD_LINE_1 = 0x80 # LCD Ram Address for 1st Line
LCD_LINE_2 = 0xC0 # LCD RAM Address for 2nd Line

#-----------------------------------------------------------------------------
# Main Function
#-----------------------------------------------------------------------------

def main():

        # Set Up Button GPIO, input w/ pulldown
        GPIO.setup(BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Previous States Initialization:
        btn_Pressed = False
        prev_IP = None
        prev_Display = None 

        LCD_Setup() # Set up/initialize LCD

        # Inform user that the RPi is waiting for IP
        LCD_String("Waiting for IP", LCD_LINE_1)
        LCD_String("Assignment...", LCD_LINE_2)

        time.sleep(3) # 3s Delay

        while True:
                pressed = GPIO.input(BTN) == 1 # Button High When Pressed

                myIPAddress = getIP() # Get IP Address
                myMACAddress = getMAC() # Get MAC Address

                if pressed:  # Button pressed
                        if prev_Display != "MAC": # If MAC is NOT being displayed
                                LCD_String("My MAC Address", LCD_LINE_1) # Print MAC Address
                                LCD_String(myMACAddress or "N/A", LCD_LINE_2)
                                prev_Display = "MAC" # New State = MAC Display
                else:  # Button released
                                # If IP exists and is not being displayed or is not up to date
                                if myIPAddress and (prev_Display != "IP" or myIPAddress != prev_IP):
                                        LCD_String("My IP Address:", LCD_LINE_1)
                                        LCD_String(myIPAddress, LCD_LINE_2) # Print IP Address
                                        prev_Display = "IP" # New State = IP Display
                                        prev_IP = myIPAddress # Update current IP
                                # If there is No IP Address & Wait is not being Displayed already
                                elif not myIPAddress and prev_Display != "WAIT":
                                        LCD_String("Waiting for IP", LCD_LINE_1)
                                        LCD_String("Assignment...", LCD_LINE_2)
                                        prev_Display = "WAIT"

                time.sleep(0.25) # 0.25s Delay

#-----------------------------------------------------------------------------
# LCD Functions 
#-----------------------------------------------------------------------------

def LCD_Setup():
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM) # GPIO = GPIO Pin #s

        # Set Pins as Outputs
        GPIO.setup(D7, GPIO.OUT)
        GPIO.setup(D6, GPIO.OUT)
        GPIO.setup(D5, GPIO.OUT)
        GPIO.setup(D4, GPIO.OUT)
        GPIO.setup(E,  GPIO.OUT)
        GPIO.setup(RS, GPIO.OUT)

        time.sleep(0.1) # 0.1s Delay

        LCD_Init() # Initialize LCD

def LCD_Init():
        # 4-bit Initialization Sequence
        GPIO.output(RS, GPIO.LOW) # Command Mode ON - Send Instructions

        # Reset using 8-bit knocks - Reset into known 8-bit state
        # Send command 3 times with delays so slow LCD will receive it
        # and reset into known 8-bit state
        write4(0x30); time.sleep(0.0005)  
        write4(0x30); time.sleep(0.0005)
        write4(0x30); time.sleep(0.0005)

        # Switch to 4-bit Mode
        write4(0x20); time.sleep(0.0005)

        # Standard LCD Setup
        LCD_Disp(0x28, LCD_cmd) # 4-bit mode w/ 2 rows
        LCD_Disp(0x08, LCD_cmd) # Display OFF
        LCD_Disp(0x01,LCD_cmd) # Clear Display
        time.sleep(0.0005)
        LCD_Disp(0x06, LCD_cmd) # Entry Mode: Increment, no Shift
        LCD_Disp(0x0C, LCD_cmd) # Display ON, Cursor OFF, Blink OFF   

def write4(value):
        # Used during setup. Takes only the upper bits of the value
        # and sends them to pins D7-D4. LCD reads the command 0x3_.
        GPIO.output(D4, bool(value & 0x10))
        GPIO.output(D5, bool(value & 0x20))
        GPIO.output(D6, bool(value & 0x40))
        GPIO.output(D7, bool(value & 0x80))
        lcd_toggle_enable()

def LCD_Disp(bits, mode):
        GPIO.output(RS, mode) # RS

        # High Bits
        GPIO.output(D4, bool(bits & 0x10))
        GPIO.output(D5, bool(bits & 0x20))
        GPIO.output(D6, bool(bits & 0x40))
        GPIO.output(D7, bool(bits & 0x80))
        lcd_toggle_enable()

        # Low Bits
        GPIO.output(D4, bool(bits & 0x01))
        GPIO.output(D5, bool(bits & 0x02))
        GPIO.output(D6, bool(bits & 0x04))
        GPIO.output(D7, bool(bits & 0x08))
        lcd_toggle_enable()

def lcd_toggle_enable():
        time.sleep(0.0005)
        GPIO.output(E, True)
        time.sleep(0.0005)
        GPIO.output(E, False)
        time.sleep(0.0005)

def LCD_String(message, line):
        message = message.ljust(LCD_Width, " ")

        LCD_Disp(line, LCD_cmd)

        for i in range(LCD_Width):
                LCD_Disp(ord(message[i]),LCD_chr)

#-----------------------------------------------------------------------------
# Get Address Functions
#-----------------------------------------------------------------------------

def getIP(): # Grab IP Address
        try:
                myIP = subprocess.run("hostname -I | awk '{print $1}'", shell=True,capture_output=True,text=True)
                return myIP.stdout.strip() # Return IP Address output (remove extra characters)
        except: # If error
                print("Error getting IP Address.")
                return None

def getMAC(): # Grab MAC Address
        try:
                myMAC = subprocess.run("ifconfig wlan0 | grep ether | awk '{print $2}'", shell=True,capture_output=True,text=True)
                return myMAC.stdout.strip() # Return MAC Address output (remove extra characters)
        except: # If error
                print("Error getting MAC Address.")
                return None

if __name__ == "__main__":
        try:
                main() # Run main function
        except KeyboardInterrupt:
                LCD_Disp(0x01, LCD_cmd) # Clear Display
                pass
        finally:
                try:
                        LCD_Disp(0x01,LCD_cmd) # Clear Display
                except Exception:
                        pass
                GPIO.cleanup()

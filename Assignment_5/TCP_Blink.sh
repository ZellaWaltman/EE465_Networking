#!/bin/bash

# LED = GPIO pin 4

# Loop for every line received/read
# Use -l for line-buffering so every packet appears right when captured
sudo tcpdump -l -nn icmp 2>/dev/null | while read line; do

        # Tcpdump, do not resolve hostnames or ports, print in HEX (-X)
        # capture 1 ICMP packet (-c 1) and send errors/startup tcpdump
        # message to /dev/null so it is hidden & doesn't clutter screen
        packet=$(sudo tcpdump -nn -X -c 1 icmp 2>/dev/null)

        # Use grep -q for quiet mode, not printing to user
        # If ICMP packet contains specific payload, do action:
        if echo "$packet" | grep -q "aaae"; then
                gpioset gpiochip0 4=1 # LED ON
        elif echo "$packet" | grep -q "abae"; then
                gpioset gpiochip0 4=0 # LED OFF
        else # If payload does not match commands
                echo "A ping message was just received."
        fi
done

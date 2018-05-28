#!/usr/bin/python 
import time
import daemon
from socket import *

def broadcast():
    fd = socket(AF_INET, SOCK_DGRAM)  
    fd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  
    fd.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)  
    data = "Hello world, this is Pi"

    while 1:
	fd.sendto(data, ('255.255.255.255', 50022))
        time.sleep(30)

if __name__ == "__main__":
    with daemon.DaemonContext():
	broadcast()


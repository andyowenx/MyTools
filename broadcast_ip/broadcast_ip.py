import time
from socket import *

fd = socket(AF_INET, SOCK_DGRAM)  
fd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  
fd.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)  

data = "Hello world"

while 1:
    fd.sendto(data, ('255.255.255.255', 50022))
    time.sleep(30)



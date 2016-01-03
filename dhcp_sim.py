import subprocess
import logging
import random 
import sys

#supress scapy warning messages
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
logging.getLogger("scapy.interactive").setLevel(logging.ERROR)
logging.getLogger("scapy.loading").setLevel(logging.ERROR)

#Module try/except block
try:
	from scapy.all import *

except ImportError:
	print"Scapy pacakge for python is not installed on your system."
	print"Get it from https://pypi.python.org/pypi/scapy and try again."
	sys.exit()


print" \n Make sure to run this program as ROOT! \n"

#Prompt for network interface
net_iface=raw_input("Enter the interface to the target network: ")

#Set the network into promiscuous mode
subprocess.call(["ifconfig",net_iface,"promisc"],stdout=None,stderr=None,shell=False)

print "\nInterface %s was set to PROMISC mode."%net_iface

#Disable scapy ip check 
conf.checkIPaddr=False



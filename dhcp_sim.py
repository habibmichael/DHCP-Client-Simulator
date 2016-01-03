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

#Create User Menu
try:
    #Enter option for the first screen
    while True:
        print "\nUse this tool to:\ns - Simulate DHCP Clients\nr - Simulate DHCP Release\ne - Exit program\n"
        
        user_option_sim = raw_input("Enter your choice: ")
        
        if user_option_sim == "s":
            print "\nObtained leases will be exported to 'DHCP_Leases.txt'!"
            
            pkt_no = raw_input("\nNumber of DHCP clients to simulate: ")
            
            pkt_inf = raw_input("Interface on which to send packets: ")
            
            print "\nWaiting for clients to obtain IP addresses...\n"
            
            try:
                #Calling the function for the required number of times (pkt_no)
                for iterate in range(0, int(pkt_no)):
                    all_leased_ips = generate_dhcp_seq()[0]
                      
                
            except IndexError:
                print "No DHCP Server detected or connection is broken."
                print "Check your network settings and try again.\n"
                sys.exit()
                
            #List of all leased IPs
            dhcp_leases = open("DHCP_Leases.txt", "w")
            
          
            #Print each leased IP to the file
            for index, each_ip in enumerate(all_leased_ips):
                #Another way to write to file
                print >>dhcp_leases, each_ip + "," + server_id[index] + "," + client_mac[index]
                
            dhcp_leases.close()
            
            continue

        elif user_option_sim == "r":
            while True:
                print "\ns - Release a single address\na - Release all addresses\ne - Exit to the previous screen\n"
                
                user_option_release = raw_input("Enter your choice: ")
                
                if user_option_release == "s":
                    print "\n"
                    
                    user_option_address = raw_input("Enter IP address to release: ")
                  
                    
                    try:
                        #Check if required IP is in the list and run the release function for it
                        if user_option_address in all_leased_ips:
                            index = all_leased_ips.index(user_option_address)

                            generate_dhcp_release(user_option_address, client_mac[index], server_id[index])
                            
                            print "\nSending RELEASE packet...\n"
                            
                        else:
                            print "IP Address not in list.\n"
                            continue
                    
                    except (NameError, IndexError):
                        print "\nSimulating DHCP RELEASES cannot be done separately, without prior DHCP Client simulation."
                        print "Restart the program and simulate DHCP Clients and RELEASES in the same program session.\n"
                        sys.exit()
                
                elif user_option_release == "a":
     
                    
                    try:
                        #Check if required IP is in the list and run the release function for it
                        for user_option_address in all_leased_ips:
                            
                            index = all_leased_ips.index(user_option_address)

                            generate_dhcp_release(user_option_address, client_mac[index], server_id[index])
                            
                    except (NameError, IndexError):
                        print "\nSimulating DHCP RELEASES cannot be done separately, without prior DHCP Client simulation."
                        print "Restart the program and simulate DHCP Clients and RELEASES in the same program session.\n"
                        sys.exit()
                    
                    print "\nThe RELEASE packets have been sent.\n"
                    
                    #Erasing all leases from the file
                    open("DHCP_Leases.txt", "w").close()
                    
                    print "File 'DHCP_Leases.txt' has been cleared."
                    
                    continue
                
                else:
                    break
            
        else:
            print "Exiting... See ya...\n\n"
            sys.exit()

except KeyboardInterrupt:
    print "\n\nProgram aborted by user. Exiting...\n"
    sys.exit()            

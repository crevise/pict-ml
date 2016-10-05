#! /usr/bin/env python

"""
To add rules to catch packets:
	sudo iptables -A OUTPUT -p tcp --dport 80 -j NFQUEUE --queue-num 1
	sudo iptables -A INPUT -p tcp --sport 80 -j NFQUEUE --queue-num 1

To delete the rules:
	sudo iptables -D OUTPUT -p tcp --dport 80 -j NFQUEUE --queue-num 1
	sudo iptables -D INPUT -p tcp --sport 80 -j NFQUEUE --queue-num 1
"""
from scapy.all import *
from netfilterqueue import NetfilterQueue
from datetime import datetime
table = {}
timestamps = {}

def filter(nfpkt):
	packet = IP(nfpkt.get_payload()) #converts the raw packet to a scapy compatible string
	if packet.haslayer(TCP) and packet.haslayer(Raw):
		http_content = packet.getlayer(Raw).load
		if packet[TCP].dport == 80:
			headers = http_content.split("\r\n\r\n")
			list_of_headers = headers[0].split("\r\n")
			table[ (packet[TCP].sport, packet[TCP].dport) ] = list_of_headers
			timestamps[ (packet[TCP].sport, packet[TCP].dport) ] = datetime.now()
		else:
			headers = http_content.split("\r\n\r\n")
			if headers[0].startswith('HTTP'):
				list_of_headers = headers[0].split("\r\n")
				timenow = datetime.now()
				print timenow - timestamps[ (packet[TCP].dport, packet[TCP].sport) ]
				#print table[ (packet[TCP].dport, packet[TCP].sport)], "==>" ,list_of_headers
	nfpkt.accept() # in real case drop the packet


def setupFilter():
	nfqueue = NetfilterQueue()
	#1 is the iptabels rule queue number, filter is the callback function
	nfqueue.bind(1, filter) 
	try:
		print "[*] waiting for data"
		nfqueue.run()
	except KeyboardInterrupt:
		pass

if __name__ == '__main__':
	setupFilter()
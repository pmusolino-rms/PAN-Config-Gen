import sys
import argparse
import socket
import ssl
import requests
import urllib3
import urllib3.contrib.pyopenssl
import logging
import ipaddress
from prettytable import PrettyTable
import ConfigParser

urllib3.contrib.pyopenssl.inject_into_urllib3()
urllib3.disable_warnings()
logging.captureWarnings(True)

try:
	config = ConfigParser.SafeConfigParser()
	config.read('config.ini')
except ConfigParser.ParsingError, err:
	print 'Cound not parse:', err

for section_name in config.sections():
	for name,value in config.items(section_name):
		if name =="url":
			URL = value
		next
		if name == "username":
			USERNAME = value
			next
		if name == "password":
			PASS = value
			next

TENANTCOMMENT='APP_01'
TENANTPREFIX='TEN'
PEERINGCOMMENT='Edge'
PEERINGPREFIX='TENANT-'

def requestsGetHandler(url,debug):
	if debug:
		print url
	try:
		response=requests.get(url,verify=False,auth=(USERNAME,PASS))
		return response
	except urllib3.exceptions.SSLError as e:
		print e

def getNetwork(tenant,prefix,comment,debug):
		r=requestsGetHandler(URL+"network?*vCloud_Network_Name~:="+prefix+tenant+"&comment~:="+comment,debug)
		if debug:
			print r
		j=r.json()
		if debug:
			print j
		if j[0].get(u'network'):
			network=(j[0].get(u'network'))
			if network is not None:
				if debug:
					print network
				networkObject=ipaddress.IPv4Network(network)
				return(networkObject)
			else:
				print "Network not found"
				sys.exit(1)

def createConfig(network,pre,fwIP,gateway,tenant,vlan):
	#create interface line
	print "set network interface aggregate-ethernet ae2 layer3 units ae2." \
		+ vlan + " comment \"Peering Edge FW to COR VDC / VRF : Tenant - " + tenant + "\" tag " + vlan \
		+ " interface-management-profile EXTERNAL-PING_ONLY ip " + fwIP + "/" + pre
	print "set network interface aggregate-ethernet ae2 layer3 units ae2." \
		+ vlan + " ipv6 neighbor-discovery router-advertisement enable no"

	#Create VR
	print "set network virtual-router RMS-MS-" + tenant + "-VR interface ae2." + vlan \
		+ " routing-table ip static-route DEFAULT destination 0.0.0.0/0 nexthop next-vr RMS-MS-CORE-VR"
	print "set network virtual-router RMS-MS-" + tenant + "-VR routing-table ip static-route TENANT-" \
		+ tenant + " destination " + str(network) + " nexthop ip-address " + gateway 

	#Update Core VR
	print "set network virtual-router RMS-MS-CORE-VR routing-table ip static-route TENANT-" \
		+ tenant + " destination " + str(network) + " nexthop next-vr RMS-MS-" + tenant + "-VR"

	#Set Vsys on interface and Zone
 	print "set vsys vsys2 import network interface ae2." + vlan + " virtual-router RMS-MS-" + tenant + "-VR"
 	print "set vsys vsys2 zone MS-" + tenant + "-COR-ZN network zone-protection-profile " \
 		+ "ZN-PROTECTION-PROFILE-TENANTS layer3 ae2." + vlan

 	#Policy
 	print "set vsys vsys2 rulebase nat rules NAT-TENANTS-ALL from MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-02_TO-INTERNET_1 from MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-03_RMSONE_RL_OUT_00 from MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-03_RMSONE_RL_OUT_01 from MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-03_RMSONE_RL_OUT_02 from MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-03_RMSONE_RL_OUT_03 from MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-03_RMSONE_RL_OUT_04 from MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-03_RMSONE_RL_OUT_05 from MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-03_RMSONE_RL_OUT_06 from MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-03_RMSONE_RL_OUT_07 from MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-03_RMSONE_RL_OUT_08 from MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-03_RMSONE_RL_OUT_09 from MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-03_RMSONE_RL_OUT_10 from MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-12_00 from MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-12_01 to MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-13_00 to MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-13_01 from MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-13_02 from MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-13_03 from MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-14_01 from MS-" + tenant + "-COR-ZN"
	print "set vsys vsys2 rulebase security rules  POLICY-14_02 from MS-" + tenant + "-COR-ZN"
	return

def main():
	x = PrettyTable(["Item","Value"])
	x.align["Item"] = "l"
	x.align["Value"] = "r"
	x.padding_width = 5
	parser = argparse.ArgumentParser(description='Generate PAN config for tenants')
	parser.add_argument('-v', '--version', action='version',version='%(prog)s (version 0.5)')
	parser.add_argument("-d", "--debug", help="Verbose output", action="store_true")
	parser.add_argument("-i", "--info", help="Just output tenant info", action="store_true")
	parser.add_argument("tenant_id", type=int)
	args = parser.parse_args()
	output = None
	debug = False
	info = False
	if args.debug:
		debug = True
	if args.info:
		info = True
	site=None
	tenant_id = args.tenant_id
	vlan_id = 0
	if (0 <= tenant_id <= 199):
		site="LHR"
		vlan_id = tenant_id + 3002
	if (200 <= tenant_id <= 399):
		site="YYZ"
		vlan_id = tenant_id + 1802
	if (tenant_id <= 0 or tenant_id >=400):
		sys.exit("Tenant ID out of bounds")
	if debug:
		print "Site: " + site
		print "Vlan ID: " + str(vlan_id)

	tenantNetwork=getNetwork(str(tenant_id),TENANTPREFIX,TENANTCOMMENT,debug).supernet(new_prefix=22)
	if debug:
		print str(tenantNetwork)

	peeringNetwork=getNetwork(str(tenant_id).zfill(3),PEERINGPREFIX,PEERINGCOMMENT,debug)
	hostList=list(peeringNetwork.hosts())
	prefix=str(peeringNetwork.prefixlen)
	firewallIP=str(hostList[0])
	defaultGW=str(hostList[-1])
	if debug:
		print "Prefix: " + prefix + "\nFirewallIP: " + firewallIP + "\nDefaultGW: "  + defaultGW
	
	if info:
		x.add_row(["Site", site])
		x.add_row(["Tenant ID", str(tenant_id).zfill(3)])
		x.add_row(["Vlan ID", str(vlan_id)])
		x.add_row(["Peering Network", str(peeringNetwork)])
		x.add_row(["Peering Default GW", defaultGW])
		x.add_row(["FW Interface ae2." + str(vlan_id), firewallIP])
		x.add_row(["Tenant Network", str(tenantNetwork)])
		print x
		sys.exit(1)

	createConfig(tenantNetwork,prefix,firewallIP,defaultGW,str(tenant_id).zfill(3),str(vlan_id))

if __name__ == "__main__":
	main()

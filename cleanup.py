#!/usr/bin/python3

import requests, os, subprocess, platform, getpass
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning


uricluster = "/cluster/"
urivm = "/vms/"
search = "?searchString="

###############################################
# DO NOT CHANGE ANYTHING BELOW THIS LINE!!!!! #
###############################################
headers = {'content-type': 'application/json'}
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
FNULL = open(os.devnull, 'w')

def ping(host):
    ping_str = "-n 1" if  platform.system().lower()=="windows" else "-c 1"
    args = "ping " + " " + ping_str + " " + host
    need_sh = False if  platform.system().lower()=="windows" else True
    return subprocess.call(args, shell=need_sh, stdout=FNULL, stderr=subprocess.STDOUT) == 0

# should convert these to try|except?
def restget(uri):
	response = requests.get(uri,auth=HTTPBasicAuth(user,passwd),headers=headers,verify=False)
	return(response)

def restpost(uri,payload):
	response = requests.post(uri,auth=HTTPBasicAuth(user,passwd),headers=headers,json=payload,verify=False)
	return(response)

def restput(uri,payload):
	response = requests.put(uri,auth=HTTPBasicAuth(user,passwd),headers=headers,json=payload,verify=False)
	return(response)

def restdelete(uri):
	response = requests.delete(uri,auth=HTTPBasicAuth(user,passwd),headers=headers,verify=False)
	return(response)

########################
# MAIN                 #
########################
if __name__ == '__main__':
	kg1 = 0
	while (kg1 == 0):
		print ("\n" * 100)
		print("This script will mercilessly delete some VMs and their snapshots. This is obviously a very destructive action!")
		cont1 = input("Are you sure you want to continue? (yes/no) ")
		if ("yes" == cont1 or "y" == cont1):
			kg1 = 1
		elif ("no" == cont1 or "n" == cont1):
			kg1 = 0
			print("Exiting...")
			raise SystemExit
		else:
			kg1 = 0
	CIP = input("Enter your cluster IP/DNS address: ")
	buri1 = "https://" + CIP + ":9440/PrismGateway/services/rest/v1"
	buri2 = "https://" + CIP + ":9440/PrismGateway/services/rest/v2.0"
	user = input("Enter your Nutanix cluster username: ")
	passwd = getpass.getpass("Enter your Nutanix cluster password: ")
	searchfilter = input("Please enter the VM search string (ex: charon): ")
	if ping(CIP):
		print("\n")
		uri = buri1 + urivm + search + searchfilter
		status = restget(uri)
		dstatus = status
		# want to see the full output of the rest call?  Uncomment this line:
		# print(status.json())
		if (status.ok):
			kg2 = 0
			while (kg2 == 0):
				print ("\n" * 100)
				print("\nList of VMs that match the search filter " + searchfilter)
				print("VM Count: " + str(status.json()['metadata']['count']))
				for a in range(len(status.json()['entities'])):
					print("VM Name: " + status.json()['entities'][a]['vmName'])
				cont2 = input("Are you absolutely sure you want to delete all of the VMs listed? (yes/no) ")
				if ("yes" == cont2 or "y" == cont2):
					kg2 = 1
					# DESTROY!
					for a in range(len(dstatus.json()['entities'])):
						print("Deleting VM: " + dstatus.json()['entities'][a]['vmName'])
						uri = buri2 + urivm + dstatus.json()['entities'][a]['uuid'] + "?delete_snapshots=true"
						#print(uri)
						status = restdelete(uri)
				elif ("no" == cont2 or "n" == cont2):
					kg2 = 0
					print("Exiting...")
					raise SystemExit
				else:
					kg2 = 0
		else:
			print("Unable to get VM list:\t ", status.json() ,"\n  Please investigate.  Exiting...")
			raise SystemExit
	else:
		print("Cannot ping cluster " + CIP)
		print("Please investigate.  Exiting...")
		raise SystemExit

print("\n")
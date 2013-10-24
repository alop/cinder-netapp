#!/usr/bin/env python
#============================================================#
#                                                            #
# $ID:$                                                      #
#                                                            #
# aggr-space.pw
# based off hello #
# Xfind who this filer is
# Xget all the disks owned by this filer
# find all disks I own that are not used
# Create an aggr from that list
#============================================================#

import sys
import time
sys.path.append("lib/NetApp")
from NaServer import *

def print_usage():
  print ("Usage: hello_ontapi.py <filer> <user> <password> \n")
  print ("<filer> -- Filer name\n")
  print ("<user> -- User name\n")
  print ("<password> -- Password\n")
  sys.exit (1)

args = len(sys.argv) - 1

if(args < 3):
  print_usage()

filer = sys.argv[1]
user = sys.argv[2]
password = sys.argv[3]

s = NaServer(filer, 1, 1)
s.set_server_type("Filer")
s.set_admin_user(user, password)
s.set_transport_type("HTTP")
system = s.invoke("system-get-info")
sysinfo = system.child_get("system-info")
sysid = sysinfo.child_get_string("system-id")

print sysid
output = s.invoke("disk-sanown-list-info")

if(output.results_errno() != 0):
   r = output.results_reason()
   print("Failed: \n" + str(r))

else :
   disks = output.child_get("disk-sanown-details")
   result = disks.children_get()

   disk_list = []
   for disk in result:
     disk_name = disk.child_get_string("name")
     owner = disk.child_get_string("owner-id")
     if owner == sysid:
        disk_list.append(disk_name)

print disk_list
aggr_disks = []

for i in disk_list:
  print "Checking details for %s" % i
  time.sleep(0.3)
  diskinfo = s.invoke("disk-list-info", "disk", i)
  details = diskinfo.child_get("disk-details")
  check_list = details.children_get()

  for j in check_list:
    disk_name = j.child_get_string("name")
    aggr = j.child_get_string("aggregate")
    if aggr is None:
      aggr_disks.append(disk_name)

print "Aggr list", aggr_disks
#Subtract some spares
aggr_disk_list = len(aggr_disks) - 2
output = s.invoke("aggr-create", "aggregate", "newaggr", "disk-count", aggr_disk_list)
if(output.results_errno() != 0):
  r = output.results_reason()
  print("Failed: \n" + str(r))
else:
  print "Success"


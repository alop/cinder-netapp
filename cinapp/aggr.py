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
import yaml
sys.path.append("lib/NetApp")
from NaServer import *

def print_usage():
  print ("Usage: hello_ontapi.py <filer> <user> <password> \n")
  print ("<filer> -- Filer name\n")
  print ("<user> -- User name\n")
  print ("<password> -- Password\n")
  sys.exit (1)

def create():
  args = len(sys.argv) - 1

  if(args < 3):
    print_usage()

  filer = sys.argv[1]
  user = sys.argv[2]
  password = sys.argv[3]

  aggr_name = "cinder_aggr"
  vol_name = "cinder"

  s = NaServer(filer, 1, 1)
  s.set_server_type("Filer")
  s.set_admin_user(user, password)
  s.set_transport_type("HTTP")

  # Get the sysid of "this" controller
  system = s.invoke("system-get-info")
  sysinfo = system.child_get("system-info")
  sysid = sysinfo.child_get_string("system-id")

  # get the disks that this controller owns
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

  aggr_disks = []

  # Make sure the disks aren't already assigned to an aggr
  for i in disk_list:
    print "Checking details for disk %s" % i
    time.sleep(0.4)
    diskinfo = s.invoke("disk-list-info", "disk", i)
    details = diskinfo.child_get("disk-details")
    check_list = details.children_get()

    for j in check_list:
      disk_name = j.child_get_string("name")
      aggr = j.child_get_string("aggregate")
      if aggr is None:
        aggr_disks.append(disk_name)

  #Subtract some spares
  aggr_disk_list = len(aggr_disks) - 2

  # Create an aggr using n - 2 available disks
  output = s.invoke("aggr-create", "aggregate", aggr_name, "disk-count", aggr_disk_list)
  if(output.results_errno() != 0):
    r = output.results_reason()
    print("Failed: \n" + str(r))
  else:
    print "Success"

  # Get maximum space
  vol_size = ""

  output = s.invoke("aggr-space-list-info", "aggregate", aggr_name)
  if(output.results_errno() != 0):
   print("Failed: " + str(output.results_reason()))
  else:
    info = output.child_get("aggr-space-info")
    vol_size = info.child_get_int("size-nominal")

# Create the cinder volume utilizing maximum space
output = s.invoke("volume-create", "containing-aggr-name", aggr_name, "size", vol_size)

if(output.results_errno() != 0):
  print("Failed: " + str(output.results_reason()))
else:
  print "Success"

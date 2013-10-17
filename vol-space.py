#!/usr/bin/env python
#============================================================#
#                                                            #
# $ID:$                                                      #
#                                                            #
# vol-space.pw
# based off hello #
# gets space used in each vol
#============================================================#

import sys
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
output = s.invoke("volume-list-info")

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

if(output.results_errno() != 0):
   r = output.results_reason()
   print("Failed: \n" + str(r))

else :
   volumes = output.child_get("volumes")
   result = volumes.children_get()

   for vol in result:
     vol_name = vol.child_get_string("name")
     vol_free = vol.child_get_int("size-available")
     print '%s has %s free' % (vol_name, sizeof_fmt(vol_free))
  


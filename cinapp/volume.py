# Create the cinder volume utilizing maximum space
output = s.invoke("volume-create", "containing-aggr-name", aggr_name, "size", vol_size)

if(output.results_errno() != 0):
  print("Failed: " + str(output.results_reason()))
else:
  print "Success"

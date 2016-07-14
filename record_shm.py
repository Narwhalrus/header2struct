import header2struct
from shm_iface import shm_wrapper
import copy
import time
import os
import csv

def append_csv_col(ifilename, ofilename, col_name, data):
  with open(ifilename, 'r') as ifile:
    with open(ofilename, 'w') as ofile:
      writer = csv.writer(ofile, lineterminator='\n') 
      reader = csv.reader(ifile)

      updated_rows = []
      row = next(reader)
      row.append(col_name)
      updated_rows.append(row)

      for i, row in enumerate(reader):
        row.append(data[i])
        updated_rows.append(row)

      writer.writerows(updated_rows)
      
# Gen struct type
print 'Generating struct...'
#mmd_to_avncs_type = header2struct.gen_struct('/usr/sim/intg/relentless/AvionicsDataServer/dev_jr/src/include/mmd_to_avncs.h', 'mmd_to_avncs_type')
mmd_to_avncs_type = header2struct.gen_struct('/home/sim/prod/Visuals/common/rsi_v2.1/src/include/q3dVisInterface.h', 'q3dVisInterface')

# Bind structure to AVNCS shared memory
print 'Binding struct to AVNCS shm...'
mmap_loc = os.getenv('CNFG')
shm = shm_wrapper(mmap_loc)
#bound_struct = shm.attach_struct('AVNCS', mmd_to_avncs_type)
bound_struct = shm.attach_struct('VIS', mmd_to_avncs_type)

print 'Recording data...'
frames = []
times = []
for i in xrange(0,1000):
  #print bound_struct.gps.latitude
  frames.append(copy.copy(bound_struct))

  times.append(time.time())
  time.sleep(0.01)
  
print 'Writing records to shm_test.csv...'
header2struct.write_csv_file('shm_test.csv', frames)
print 'Appending time col to shm_test_w_time.csv...'
append_csv_col('shm_test.csv', 'shm_test_w_time.csv', 'time', times)

  

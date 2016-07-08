import header2struct as h2s
import os

if True:
  # Create binary file
  os.system('./blah')

# Create type
my_type = h2s.gen_struct('test.h', 'nd_struct')

# Convert binary file to csv
h2s.bin2csv('outbin.bin', 'test.csv', my_type)

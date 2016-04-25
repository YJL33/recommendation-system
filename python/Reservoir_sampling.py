"""
Reservoir sampling
"""
#!/usr/bin/python

import sys
import time
import random

start = time.time()

if len(sys.argv) == 4:
    f_in = open(sys.argv[2],'r')        # file to be sample
    f_out = open(sys.argv[3],'w')       # sample
elif len(sys.argv) == 2:
    f_in = sys.stdin;
else:
    sys.exit("Usage:  python samplen.py <lines> <?file>")
 
N = int(sys.argv[1]);    # sample size
sample = [];
 
for i,line in enumerate(f_in):
    if i < N:
        sample.append(line)
    elif i >= N and random.random() < N/float(i+1):
        replace = random.randint(0,len(sample)-1)
        sample[replace] = line
 
for line in sample:
    #sys.stdout.write(line)
    f_out.write("%s" % line)

print ("--- %s seconds ---" % str(time.time()-start))
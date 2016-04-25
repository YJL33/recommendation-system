"""
Verify the recommended answer
"""

import sys
import Recommendation_minhash as RecMin
#import Recommendation_simhash as RecSim

if len(sys.argv) == 4:
    print "Generating Pickle"
    RecMin.item2itemMinhashRec(sys.argv[1], sys.argv[2], sys.argv[3])

if len(sys.argv) == 5:
    rec1, rec2 = RecMin.item2itemMinhashRec(sys.argv[1], sys.argv[2], sys.argv[3])
    print "Verify: "
    ans = RecMin.getPoiBasket(sys.argv[1], sys.argv[4])
    cnt1 = 0
    cnt2 = 0
    for i in rec1:
        if i in ans:
            cnt1 += 1
    print "avg distance hit: %d/5" % cnt1
    for j in rec2:
        if j in ans:
            cnt2 += 1
    print "min distance hit: %d/5" % cnt2

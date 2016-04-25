"""
USC-XXXXXX data challenge

using item-to-item recommendation and simhash to recommend 5 items to person of interest (poi)

1. read all user record into a dictionary
2. apply simhash, the hashed record can be pickled for later use
3. read poi's shopping basket
4. recommend the poi the most similar items
   (according to the distance between each item that poi bought and all other items)

input: poi id, raw training file, and hashed records (if any)
output: top 10 similar item (for each item)
"""
import re
import sys
import time
import cPickle as pickle
import heapq
from simhash import Simhash

start = time.time()

def distance(one, another):                 # Get distance of two simhash
    x = (one ^ another) & ((1 << 64) - 1)
    ans = 0
    while x:
        ans += 1
        x &= x - 1
    return ans

def getRec(user_record):
    myDict = {}                     # Read all user records into dictionary
    f = open(user_record, 'r')
    print "###### Phase 1. ######\nloading user record..."
    for l in f:
        ls = l.split('\x01')        # Original format: user SKU qty  ^A \x01
        if ls[1] not in myDict:
            myDict[ls[1]] = ls[0]     # sku = key, user = value
        else:
            myDict[ls[1]] += " " + ls[0]         # add user into values
    print "found %s items, eclipsed time: %s sec." % (str(len(myDict)), str(time.time()-start))
    return myDict

def applySimhash(rec_dict):                 # Apply simhash
    print "###### Phase 2. ######\napplying simhash..."

    for k, v in rec_dict.items():
        rec_dict[k] = Simhash(v).value
    print "simhash completed, eclipsed time: %s sec." % str(time.time()-start)
    return rec_dict

def getPoiBasket(customer_id, user_record):     # Read poi's shopping basket from raw data
    poi_baskets = []
    print "###### Phase 3. ######\nchecking poi's basket..."
    f = open(user_record, 'r')
    for l in f:
        ls = l.split('\x01')        # Original format: user SKU qty  ^A \x01
        if ls[0] == customer_id: poi_baskets.append(ls[1])
    print "poi has bought: ", poi_baskets
    return poi_baskets

def recommendTopFive(list_of_items, sim_dict):       # recommend top 5 items based on distance
    print "###### Phase 4. ######\ncalculating distance..."
    recommend_list = []         # Recommendation list
    tempDict = {}               # store the distance between all other items to each poi's item
    for item in list_of_items:               # Consider only items in poi's basket
        others = [one for one in sim_dict.keys() if one not in list_of_items]    # all other items
        for com in others:
            dist = distance(sim_dict[item], sim_dict[com])
            if com not in tempDict: tempDict[com] = dist        # store the distance
            else: tempDict[com] = min(tempDict[com], dist)      # update the distance
        #if len(dist_dict[item]) < 10: print "sku %s has <10 similar items" % str(item)
    recommend_list = heapq.nsmallest(5, tempDict, key=tempDict.get)
    print "recommend user %s: " % str(sys.argv[1]), recommend_list
    print "distance = ", [tempDict[com] for com in recommend_list]
    return recommend_list

# Below this line is the main part
if len(sys.argv) < 3:
    print "argv[1] = user_id\nargv[2] = raw data\nargv[3] = pickled hashed record (if any)"
    quit()
if len(sys.argv) == 3:                                  # Use the sample
    print "...directly use the raw data, beware of the size of sample"
    simhash_dict = applySimhash(getRec(sys.argv[2]))
if len(sys.argv) == 4 and sys.argv[1] != '0':           # Use the pre-hashed record
    print "...use pickled hashed record"
    simhash_dict = pickle.load(open(sys.argv[3], "rb"))
if len(sys.argv) == 4 and sys.argv[1] == '0':           # Developer mode: output hashed record only
    print "...retrieve dictionary only"
    simhash_dict = applySimhash(getRec(sys.argv[2]))
    pickle.dump(simhash_dict, open(sys.argv[3], "wb" ), pickle.HIGHEST_PROTOCOL)
    quit()

poi_baskets = getPoiBasket(sys.argv[1], sys.argv[2])
recommendation_list = recommendTopFive(poi_baskets, simhash_dict)

print ("--- %s seconds ---" % str(time.time()-start))
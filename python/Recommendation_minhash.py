"""
USC-XXXXXX data challenge

using item-to-item recommendation and minhash to recommend 5 items to person of interest (poi)

1. read all user record into a dictionary
2. apply minhash, the hashed record can be pickled for later use
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
import math

start = time.time()

def getRec(user_record):
    myDict = {}                     # Read all user records into dictionary
    f = open(user_record, 'r')
    print "###### loading user record ######"
    for l in f:
        ls = l.split('\x01')        # Original format: user SKU qty  ^A \x01
        if ls[1] not in myDict:
            myDict[ls[1]] = [int(ls[0])]     # sku = key, user = value
        else:
            myDict[ls[1]].append(int(ls[0]))         # add user into values
    print "found %s items, eclipsed time: %s sec." % (str(len(myDict)), str(time.time()-start))
    return myDict

def applyMinhash(rec_dict):                 # Apply minhash
    print "###### applying minhash ######"
    seeds = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,
             109,113,127,131,137,139,149,151,157,163,167,173,179,181,191,193,197,199,211,223,227,
             229,233,239,241,251,257,263,269,271,277,281,283,293,307,311,317,331,337,347,349,353,
             359,367,373,379,383,389,397,401,409,419,421,431,433,439,443,449,457,461,463,467,479,
             487,491,499,503,509,521,523,541,547,557,563,569,571,577,587,593,599,601,607,613,617,
             619,631,641,643,647,653,659,661,673,677,683,691,701,709,719,727,733,739,743,751,757,
             761,769,773,787,797,809,811,821,823,827,829,839,853,857,859,863,877,881,883,887,907,
             911,919,929,937,941,947,953,967,971,977,983,991,997,1009,1013,1019,1021,1031,1033,
             1039,1049,1051,1061,1063,1069,1087,1091,1093,1097,1103,1109,1117,1123,1129,1151,1153,
             1163,1171,1181,1187,1193,1201,1213,1217,1223,1229,1231,1237,1249,1259,1277,1279,1283,
             1289,1291,1297,1301,1303,1307,1319,1321,1327,1361,1367,1373,1381,1399,1409,1423,1427,
             1429,1433,1439,1447,1451,1453,1459,1471,1481,1483,1487,1489,1493,1499,1511,1523,1531,
             1543,1549,1553,1559,1567,1571,1579,1583,1597,1601,1607,1609,1613,1619]
    for k, v in rec_dict.items():
        templist = []
        for s in seeds:
            templist.append(min(sku%s for sku in v))
        rec_dict[k] = templist
    print "minhash completed, eclipsed time: %s sec." % str(time.time()-start)
    return rec_dict

def getPoiBasket(customer_id, user_record):     # Read poi's shopping basket from raw data
    poi_baskets = []
    print "###### checking poi's basket ######"
    f = open(user_record, 'r')
    for l in f:
        ls = l.split('\x01')        # Original format: user SKU qty  ^A \x01
        if ls[0] == customer_id: poi_baskets.append(ls[1])
    print "poi has bought: ", poi_baskets
    return poi_baskets

def distanceSQ(one, another):         # Return the # of difference between two
    assert len(one) == len(another)
    ans = 0
    for i, j in zip(one, another):
        if i != j: ans += 1
    return ans

def recommendTopFive(bskt, hshdct):       # recommend top 5 items based on distance
    print "###### calculating distance ######"
    rec_list = []         # Recommendation list
    avgdct = {}           # store the distance between all other items to each poi's item
    mindct = {}
    for item in bskt:               # Consider only items in poi's basket
        others = [one for one in hshdct.keys() if one not in bskt]  # all other items
        for com in others:
            dist = distanceSQ(hshdct[item], hshdct[com])
            if com not in avgdct:
                avgdct[com] = dist
                mindct[com] = dist                      # store the distance
            else:
                avgdct[com] += dist
                mindct[com] = min(mindct[com], dist)    # update the distance
        #if len(dist_dict[item]) < 10: print "sku %s has <10 similar items" % str(item)
    rec_list_avg = heapq.nsmallest(5, avgdct, key=avgdct.get)
    rec_list_min = heapq.nsmallest(5, mindct, key=mindct.get)
    print "Based on avg distance, recommend user %s: " % str(sys.argv[1]), rec_list_avg
    print "Based on min distance, recommend user %s: " % str(sys.argv[1]), rec_list_min
    avg_dist = [math.sqrt(avgdct[com])/(len(bskt)*len(hshdct[com])) for com in rec_list_avg]
    print "avg dist. = ", ["{0:0.4f}".format(i) for i in avg_dist]
    min_dist = [math.sqrt(mindct[com])/(len(bskt)*len(hshdct[com])) for com in rec_list_min]
    print "min dist. = ", ["{0:0.4f}".format(i) for i in min_dist]
    return rec_list_avg, rec_list_min

def item2itemMinhashRec(poi, raw_training_file, hashed_record=None):
    """
    poi: ID of person of interest, (e.g. 3175866) in this challenge the # of id could > 20m
    raw_training_file: raw file or sample file
    hashed_record: pickled dictionary.
    """
    # Below this line is the main part
    if raw_training_file == None or poi == None:
        print "...oops! wrong argument"
        quit()
    if hashed_record == None:                                  # Use the sample
        print "...directly use the raw data, beware of the size of sample"
        minhash_dict = applyMinhash(getRec(raw_training_file))
    if hashed_record != None and poi != '0':           # Use the pre-hashed record
        print "...use pickled hashed record"
        minhash_dict = pickle.load(open(hashed_record, "rb"))
    if hashed_record != None and poi == '0':           # Developer mode: output hashed record only
        print "...retrieve dictionary only"
        minhash_dict = applyMinhash(getRec(raw_training_file))
        pickle.dump(minhash_dict, open(hashed_record, "wb" ), pickle.HIGHEST_PROTOCOL)
        quit()

    poi_baskets = getPoiBasket(poi, raw_training_file)
    recommendation_list_avg, recommendation_list_min = recommendTopFive(poi_baskets, minhash_dict)

    print ("--- %s seconds ---" % str(time.time()-start))
    return recommendation_list_avg, recommendation_list_min

##########


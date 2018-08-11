import copy

import pandas as pd
from FairDB.utils.read_data import *

import FairDB.modules.infotheo.info_theo as info
from FairDB.utils.util import *


def get_respon2(data,treatment, outcome, covariates):
    resp1 = dict()
    resp2 = dict()
    temp = covariates.copy()
    if treatment[0] in covariates:
        covariates.remove(treatment[0])
    inf=info.Info(data)
    base=inf.CMI(treatment[0],outcome[0])
    for att in covariates:
        temp.remove(att)
        after = inf.CMI(treatment[0], outcome[0], att)
        loss = (base - after)
        if loss>0:
          resp1[att] = loss
          temp.insert(0, att)
        else:
          resp2[att] = loss
    total=0
    for key,value in resp1.items():
        total+=value
    sum=0
    for key, value in resp1.items():
        resp1[key]=value/total
        sum+=resp1[key]
    total = 0
    for key,value in resp2.items():
        total+=value
    sum=0
    for key, value in resp2.items():
        resp2[key]=value/total
        sum+=resp2[key]
    sorted_x1 = reversed(sorted(resp1.items(), key=lambda e: e[1]))
    sorted_x2 = reversed(sorted(resp2.items(), key=lambda e: e[1]))
    return dict(sorted_x1),dict(sorted_x2)

def get_respon(data,treatment, outcome, covariates):
    resp = dict()
    temp = covariates.copy()
    if treatment[0] in covariates:
        covariates.remove(treatment[0])
    inf=info.Info(data)
    base=inf.CMI(treatment[0],covariates)
    for att in covariates:
        temp.remove(att)
        after = inf.CMI(treatment[0], temp,att)
        loss = (base - after)
        print(base)
        print(loss)
        resp[att] = loss
        temp.insert(0, att)
    total=0
    for key,value in resp.items():
        total+=value
    sum=0
    for key, value in resp.items():
        resp[key]=value/total
        sum+=resp[key]
    sorted_x = reversed(sorted(resp.items(), key=lambda e: e[1]))
    return dict(sorted_x)

def adjust_overlap(data,treatment, cov):
    if isinstance(treatment,str):
        treatment=[treatment]
    treatmentlevel=get_distinct(data,treatment)
    ovelap = data.groupby(cov).agg({treatment[0]: pd.Series.nunique}).reset_index()
    if ovelap.empty:
        print('No Overlap wrt. ', cov)
        return None
    ovelap.rename(columns=lambda x: x.replace(treatment[0], 'counts'), inplace=True)
    x = copy.copy(cov)
    x.insert(0, 'counts')
    pruned = data.merge(ovelap[x], on=cov, how='inner')
    pruned = pruned[pruned['counts'] == treatmentlevel]
    n1 = len(pruned.index)
    n2 = len(data.index)
    #n1=treatmentlevel
    #n2 = get_distinct(pruned, cov)
    val = pd.DataFrame({'counts': pruned.groupby(treatment).size()}).reset_index()
    return [(n1 / n2) * 100, pruned, n1, n2, val['counts'].values]


def matching(data,treatment,outcome,cov,threshould=0):
    rank=get_respon(data, treatment, outcome, cov)
    inf=info.Info(data)
    #for att in cov:
    #    rank[att] = inf.CH(treatment,att)
    cov = top_kdict(rank, len(rank))
    adj_set = cov.copy()
    ## to-do compute subclasses here
    pruned, overlapped, after, before, min= adjust_overlap(data,treatment,adj_set)
    treatment = treatment[0]
    while pruned < threshould:
        adj_set.remove(adj_set[0])
        if adj_set:
            pruned, overlapped, after, before, min = adjust_overlap(data, treatment, adj_set)
        else:
            return None
    return overlapped,adj_set,pruned


if __name__ == '__main__':
    data=read_from_csv('/Users/babakmac/Documents/XDBData/binadult.csv')
    data=read_from_db('qexpriment718')
    treatment = ['carrier']
    outcome = ['delayed']
    cov=['origin']
    overlapped, adj_set, pruned=matching(data,treatment, outcome,cov,threshould=90)
    print(adj_set)
    #overlapped, adj_set, pruned = matching(data, treatment, outcome, cov, threshould=50)
    #print(adj_set)
    #overlapped, adj_set, pruned = matching(data, treatment, outcome, cov, threshould=10)
    #print(adj_set)
    X=get_respon(data,treatment, outcome,cov)
    print(X)



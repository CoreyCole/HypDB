
from  math import *

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.special as special
from FairDB.utils.read_data import read_from_csv
# from rpy2.robjects.packages import importr
import FairDB.modules.infotheo.info_theo as info
from FairDB.utils.util import get_distinct,remove_dup
# from rpy2 import robjects as ro
import time
import random
import sys
from numpy import ceil,convolve,histogram,sqrt
from random import randrange,choices
from scipy.special import entr
from scipy.stats import chi2

def entropy(X,base=e):

    #x=data[X].values
    #x=x.flatten()
    #freqlist = np.bincount(x)
    total=np.sum(X)
    probs =np.divide(X,total)
    ent=entr(probs)
    return np.sum(ent)



def bootstrap_ci_ct(data, stat, num_samples=10000, conf=0.95):
    """
    Bootstrap confidence interval computation on a contingency table
    Parameters
    ----------
    data :
        Contingency table collected from independent samples
    stat :
        Statistic to bootstrap. Takes a contingency table as argument
    num_samples :
        Number of bootstrap samples to generate
    conf :
        Confidence level for the interval
    Returns
    -------
    ci_low :
        The lower level of the confidence interval
    ci_high :
        The upper level of the confidence interval
    """
    if isinstance(data, pd.DataFrame):
        data = data.values

    dim = data.shape
    data = data.flatten()
    data += 1
    n = data.sum()

    # print 'Bootstrap on data of size {}'.format(n)
    probas = (1.0*data)/n

    # Obtain `num_samples' random samples of `n' multinomial values, sampled
    # with replacement from {0, 1, ..., n-1}. For each sample, rebuild a
    # contingency table and compute the stat.
    temp = np.random.multinomial(n, probas, size=num_samples)
    bs_stats = [row.reshape(dim) for row in temp]
    bs_stats = [stat(ct) for ct in bs_stats]

    alpha = 1-conf
    ci_low = np.percentile(bs_stats, 100*alpha/2)
    ci_high = np.percentile(bs_stats, 100*(1-alpha/2))

    return ci_low, ci_high


def ci_mi(g, dof, n, conf):

    p_low = 1-(1-conf)/2
    p_high = (1-conf)/2

    g_low = special.chndtrinc(g, dof, p_low)
    g_high = special.chndtrinc(g, dof, p_high)
    ci_low, ci_high = ((g_low+dof)/(2.0*n), (g_high+dof)/(2.0*n))
    return ci_low, ci_high

def ztst_proportion_two_samples(m1, v1, n1, m2, v2, n2, x=0, tail=1):
        z1 = ((m1 - m2) - x)
        z2 = sqrt((v1 / n1) + (v2 / n2))
        z_score = abs(z1) / z2
        p_value = stats.norm.cdf(z_score)
        p_value *= 2
        return p_value, z_score


def shuffle(data, x,z=[],groups=[]):
    df=data
    if z:
        df[x[0]]=groups.transform(np.random.permutation)
        #df[x] = df[x].transform(np.random.permutation)
    else:
        df[x]=df[x].transform(np.random.permutation)
    return df

def fast_permutation_tst_cmi4(data, x, y, z=[], ratio=0.5, pvalue=0.05, num_samples=5000, debug=False,
                              fraction=1,optimized=False):
    if isinstance(x, str):
        x = [x]
    if isinstance(y, str):
        y = [y]
    Rstats = importr('stats')
    r2dtable = ro.r['r2dtable']
    R = ro.r
    record = []
    k = 0
    localsample=100
    start = time.time()
    stat_0=info.Info.CMI(data, x ,y, z)
    if z:
        if isinstance(z, str):
            z = [z for z in z.split(",")]
        res=dict()
        size=len(data.index)
        grouped = data.groupby(z+y+z)
        groupedsize=grouped.size()
        groupedname = groupedsize.index.values
        grouplist=groupedsize.tolist()
        pro=list()
        total=sum(grouplist)
        inclutiondic=dict()
        frac = fraction
        for item in grouplist:
            pro.insert(0, item / total)
            #print(item / total)
        pro.reverse()
        #prob=0 #groupedsize.tolist()/len(groupedsize.tolist())
        if len(groupedname)>100:
            #sampledgroups=data.groupby(z).apply(lambda x: x.sample(frac=.1))
            sampledgroups=groupedsize.sample(frac=frac, replace=False) #weights=pro
        else:
            sampledgroups = groupedsize
            #sampledgroups=groupedsize
            #sampledgroups=np.random.choice(groupedname, 100,replace=False,p=pro)
            #print('########################')
            #print(sum(pro)*total)
            #print(len(groupedsize.index.values))
            #print(len(sampledgroups.index.values))
            #print('########################')
            #for groups in np.nditer(sampledgroups):
            #  print(groups)
        #print(sampledgroups)
        ##samplesize=len(groupedsize.index.values)
        #orgsize = len(sampledgroups.index.values)
        i=0
        residual=0
        for name in sampledgroups.index.values:
             tmp=sampledgroups[name]
             inclusion=frac #(tmp/total)/
             subgroup=grouped.get_group(name)
             groupsize = len(subgroup.index)
             a=subgroup.groupby(x).size()
             b = subgroup.groupby(y).size()
             if not len(a)>=2 or not len(b)>=2:
                 h_a = entropy(a)
                 h_b = entropy(b)
                 c = subgroup.groupby(x+y).size()
                 residual+=((h_a+h_b-entropy(c))*groupsize/size)/inclusion
                 continue
             a = R('c' + str(tuple(a)))
             b = R('c' + str(tuple(b)))
             h_a = entropy(a)
             h_b = entropy(b)
             samples = r2dtable(localsample, a, b)
             record=[]
             for sample in samples:
                 freq = np.array(sample).flatten()
                 groupsize1 = freq.sum()
                 #print(inclusion)
                 mi_z = ((h_a+h_b-entropy(freq.tolist()))*groupsize/size)/inclusion
                 record.insert(0,mi_z)
             res[name]=record
        print(i)
        record=[]
        end = time.time()
        print('time')
        print(end - start)
        for i in range(0, num_samples):
            cmi=residual
            for item in res.keys():
                cmi+=res[item][random.randint(0, localsample-1)]
            record.insert(0, cmi)
            # compute number of time that we get a permutation mi greater than the sample mutual information
            k += stat_0 <= cmi
    else:
        a = data.groupby(x).size()
        b = data.groupby(y).size()
        c= data.groupby(x+y).size()
        h_a=entropy(a)
        h_b=entropy(b)
        h_ab = entropy(c)
        stat_0=h_a+h_b-h_ab
        a=R('c'+str(tuple(a)))
        b=R('c' + str(tuple(b)))
        samples=r2dtable(num_samples,a,b)
        for sample in samples:
            freq=np.array(sample).flatten()
            mi = h_a+h_b-entropy(freq.tolist())
            record.insert(0, mi)
            # compute number of time that we get a permutation mi greater than the sample mutual information
            k += stat_0 <= mi
    if debug:
        print(x)
        print(y)
        print(z)
        print(stat_0)
        print(k)
        plt.hist(record)
        plt.show()
        #time.sleep(1)
        #plt.close()

    pval = (1.0*k) / num_samples
    ci_low=pval-1.96 * sqrt(pval*(1-pval)/num_samples)
    ci_hight=pval+1.96 * sqrt(pval*(1-pval)/num_samples)
    print("#####")
    print((ci_low,ci_hight))
    print("#####")
    return [max(ci_hight, 1.0/num_samples),stat_0]


def con_permutation_tst_cmi(data, x, y, z=[], ratio=0.5, pvalue=0.05, num_samples=5000, debug=False,
                              fraction=1,optimized=False):
    if isinstance(x, str):
        x = [x]
    if isinstance(y, str):
        y = [y]
    Rstats = importr('stats')
    r2dtable = ro.r['r2dtable']
    R = ro.r
    record = []
    k = 0
    localsample=100
    start = time.time()
    stat_0=info.Info.CMI(data, x ,y, z)
    if z:
        if isinstance(z, str):
            z = [z for z in z.split(",")]
        res=dict()
        size=len(data.index)
        grouped = data.groupby(z)
        groupedsize=grouped.size()
        groupedname = groupedsize.index.values
        grouplist=groupedsize.tolist()
        pro=list()
        total=len(grouplist)
        inclutiondic=dict()
        frac = fraction
        for item in grouplist:
            pro.insert(0, item / total)
            #print(item / total)
        pro.reverse()
        #prob=0 #groupedsize.tolist()/len(groupedsize.tolist())
        sampledgroups = groupedsize
        if fraction!=1:
           if len(groupedname)>100:
                #sampledgroups=data.groupby(z).apply(lambda x: x.sample(frac=.1))
                sampledgroups=groupedsize.sample(n=int(frac*total), replace=False) #weights=pro
        else:
            pass
            #sampledgroups=groupedsize
            #sampledgroups=np.random.choice(groupedname, 100,replace=False,p=pro)
            #print('########################')
            #print(sum(pro)*total)
            #print(len(groupedsize.index.values))
            #print(len(sampledgroups.index.values))
            #print('########################')
            #for groups in np.nditer(sampledgroups):
            #  print(groups)
        #print(sampledgroups)
        i=0
        residual=0
        hist_list=0
        for name in sampledgroups.index.values:
             tmp=sampledgroups[name]
             inclusion=fraction# (tmp/total)
             subgroup=grouped.get_group(name)
             groupsize = len(subgroup.index)
             a=subgroup.groupby(x).size()
             b = subgroup.groupby(y).size()
             if not len(a)>=2 or not len(b)>=2:
                 h_a = entropy(a)
                 h_b = entropy(b)
                 c = subgroup.groupby(x+y).size()
                 residual+=((h_a+h_b-entropy(c))*groupsize/size)/inclusion
                 continue
             a = R('c' + str(tuple(a)))
             b = R('c' + str(tuple(b)))
             h_a = entropy(a)
             h_b = entropy(b)
             #print('table generation')
             start = time.time()
             samples = r2dtable(localsample, a, b)
             end = time.time()
             #print('time')
             #print(end - start)
             #print('table generated')
             i+=1
             sys.stdout.write("Permuted samples ... %s%%\r" % (i*100/len(grouped)))
             sys.stdout.flush()
             record=[]
             for sample in samples:
                 freq = np.array(sample).flatten()
                 groupsize1 = freq.sum()
                 #print(inclusion)
                 mi_z = ((h_a+h_b-entropy(freq.tolist()))*groupsize/size)/inclusion
                 record.insert(0,mi_z)
             if hist_list:
                 hist=histogram(record,bins=100, normed=True)
                 hist_list=convolve(hist,hist_list)
             else:
                 hist_list=histogram(record,bins=100, normed=True)
             #plt.plot(X)
             #plt.show()
             print(X)
             res[name]=record
        #print(i)
        record=[]
        end = time.time()
        print('time')
        print(end - start)
        for i in range(0, num_samples):
            cmi=residual
            for item in res.keys():
                cmi+=res[item][random.randint(0, localsample-1)]
            record.insert(0, cmi)
            # compute number of time that we get a permutation mi greater than the sample mutual information
            k += stat_0 <= cmi
    else:
        a = data.groupby(x).size()
        b = data.groupby(y).size()
        c= data.groupby(x+y).size()
        h_a=entropy(a)
        h_b=entropy(b)
        h_ab = entropy(c)
        stat_0=h_a+h_b-h_ab
        a=R('c'+str(tuple(a)))
        b=R('c' + str(tuple(b)))
        samples=r2dtable(num_samples,a,b)
        for sample in samples:
            freq=np.array(sample).flatten()
            mi = h_a+h_b-entropy(freq.tolist())
            record.insert(0, mi)
            # compute number of time that we get a permutation mi greater than the sample mutual information
            k += stat_0 <= mi
    if debug:
        print(x)
        print(y)
        print(z)
        print(stat_0)
        print(k)
        plt.hist(record)
        plt.show()
        #time.sleep(1)
        #plt.close()

    pval = (1.0*k) / num_samples
    ci_low=pval-1.96 * sqrt(pval*(1-pval)/num_samples)
    ci_hight=pval+1.96 * sqrt(pval*(1-pval)/num_samples)
    print("#####")
    print(k)
    print((ci_low,ci_hight))
    print("#####")
    return [max(ci_hight, 1.0/num_samples),stat_0]

def   generate_permuated_mi2(x_margin,y_margin,prob,n):
    r2dtable = ro.r['r2dtable']
    R = ro.r
    x_margin = R('c' + str(tuple(x_margin)))
    y_margin = R('c' + str(tuple(y_margin)))
    samples = r2dtable(n, x_margin, y_margin)
    record = []
    for sample in samples:
        freq = np.array(sample).flatten()
        mi_z = ((entropy(x_margin) + entropy(y_margin) -
                 entropy(freq.tolist())) * prob)
        record.insert(0, mi_z)
    ''' 
    if len(np.unique(mi_z))<10:
        print(len(np.unique(mi_z)))
        print(mi_z)
    '''
    return record


def   generate_permuated_mi(grouped,name,x,y,localsample,size,fraction):
    r2dtable = ro.r['r2dtable']
    R = ro.r
    subgroup = grouped.get_group(name)
    groupsize = len(subgroup.index)
    a = subgroup.groupby(x).size()
    b = subgroup.groupby(y).size()
    residual=0
    #print(groupsize)
    #print(name,a,b,groupsize)
    if not len(a) >= 2 or not len(b) >= 2:
        h_a = entropy(a)
        h_b = entropy(b)
        c = subgroup.groupby(x + y).size()
        residual += (h_a + h_b - entropy(c)) * groupsize / size *1/fraction
        return residual
    a = R('c' + str(tuple(a)))
    b = R('c' + str(tuple(b)))
    h_a = entropy(a)
    h_b = entropy(b)
    if sum(a)!=sum(b):
        return 0
    samples = r2dtable(localsample, a, b)
    #sys.stdout.write("Permuted samples ... %s%%\r" % (i * 100 / len(grouped)))
    #sys.stdout.flush()
    record = []
    for sample in samples:
        freq = np.array(sample).flatten()
        mi_z = ((h_a + h_b - entropy(freq.tolist())) * groupsize / size)
        record.insert(0, mi_z)
    return record


def smart_fast_permutation_tst_cmi4(data, x, y, z=[], ratio=0.5, pvalue=0.05, num_samples=5000, debug=False,
                                    fraction=1, optimized=False):
    start = time.time()
    if isinstance(x, str):
        x = [x]
    if isinstance(y, str):
        y = [y]
    Rstats = importr('stats')
    r2dtable = ro.r['r2dtable']
    R = ro.r
    record = []
    k = 0
    localsample=100
    start = time.time()
    stat_0=info.Info.CMI(data, x ,y, z)
    if z:
        if isinstance(z, str):
            z = [z for z in z.split(",")]
        res=dict()
        size=len(data.index)
        row_num=get_distinct(data,x)
        col_num=get_distinct(data, y)
        grouped = data.groupby(z)
        groupedsize=grouped.size()
        df=pd.DataFrame({'group':groupedsize.index.values, 'size':groupedsize.values})
        df=df.sort_values(by=['size'],ascending=False)
        groupedname = groupedsize.index.values
        grouplist=groupedsize.tolist()
        pro=list()
        total=len(grouplist)
        residual=0
        entropy_vector=dict()
        sample_cont_tables=dict()
        indicator=dict()
        if debug:
          print(stat_0)
        counter = 0
        totalgroups=len(grouplist)
        if debug:
            print('initialization time')
            print(end - start)
        start=time.time()
        for name in df['group']:
            counter+=1
            p=len(indicator.keys())
            #print(p)
            if len(indicator.keys())==num_samples-1:
                #pass
                break
            if sum(indicator.values()) >= pvalue*num_samples:
                pass
                #break
            subgroup = grouped.get_group(name)
            groupsize = len(subgroup.index)
            if groupsize<2:
                break
            #print(groupsize)
            for i in range(1, num_samples):
               if i in entropy_vector.keys():
                   if entropy_vector[i] >= stat_0:
                       indicator[i]=1
                       #print(i,counter)
                       continue
                   #upper_bound=groupsize/size*1.3+entropy_vector[i]
                   #print(groupsize,entropy_vector[i],upper_bound,entropy([1,1,1,1]))
                   #upper_bound=100
                   #if upper_bound<stat_0:
                   #    indicator[i] = 0
                       #print(upper_bound)
                   #    continue
               if  name not in sample_cont_tables.keys():
                        ran_mi=generate_permuated_mi(grouped,name,x,y,localsample,size,fraction)
                        ran_mi=0
                        sample_cont_tables[name]=ran_mi
               else:
                   ran_mi=sample_cont_tables[name]
               if i not in entropy_vector.keys():
                  if ran_mi==0:
                      entropy_vector[i]=0
                  else:
                      entropy_vector[i]= ran_mi[randrange(0,localsample)]
               else:
                  if ran_mi==0:
                      entropy_vector[i]+=0
                  else:
                      entropy_vector[i]+=ran_mi[randrange(0,localsample)]
            #print(df[df.loc[df['group'].isin(name)]])
    #for i in entropy_vector.values():
    #    if i>=stat_0:
    #      k+=1
    if debug:
        print('sampling completed')
        print(end - start)
    k=sum(list(indicator.values()))
    x=list(entropy_vector.values())
    if debug:
      print(indicator)
    if debug:
        plt.hist(x)
        plt.show()
    pval = (1.0*k) / num_samples
    ci_low=pval-1.96 * sqrt(pval*(1-pval)/num_samples)
    ci_hight=pval+1.96 * sqrt(pval*(1-pval)/num_samples)
    if debug:
        print("#####")
        print(k)
        print((ci_low,ci_hight))
        print("#####")
    return [max(ci_hight, 1.0/num_samples),stat_0]




def get_max_mi(x_marginal,y_marginal):
    #y_marginal=sorted(y_marginal,reverse=False)
    #x_marginal = sorted(x_marginal, reverse=True)
    total=sum(x_marginal)
    h_a=0
    for x in x_marginal:
        if x:
          h_a+=-x/total *log(x/total)
    h_b=0
    for x in y_marginal:
      if x:
        h_b+=-x/total *log(x/total)
    return min(h_a,h_b)

    if len(x_marginal)<2 or len(y_marginal)<2:
        return 0
    a=x_marginal.copy()
    b = y_marginal.copy()
    row_number=len(a)
    col_number=len(b)
    counter=0
    M = np.full([row_number, col_number], 0)
    for i in range(row_number-1,0, -1):
       col_counter=0
       row_counter = i
       counter-=1
       for j in range(col_number, 0, -1):
             if row_counter>=0 and col_counter<=col_number-1:
                 #print(row_counter, col_counter)
                 can=min(a[row_counter],b[col_counter])
                 M[row_counter,col_counter]=can
                 #print(M)
                 a[row_counter]-=can
                 b[col_counter]-=can
                 row_counter-=1
                 col_counter+=1
    counter=0
    for i in range(row_number - 1, 0, -1):
           col_counter = 1+counter
           row_counter = row_number-1
           counter += 1
           for j in range(0, col_number-col_counter, 1):
               if row_counter >= 0 and col_counter <= col_number - 1:
                   #print(row_counter, col_counter)
                   can = min(a[row_counter], b[col_counter])
                   M[row_counter, col_counter] = can
                   #print(M)
                   a[row_counter] -= can
                   b[col_counter] -= can
                   row_counter -= 1
                   col_counter += 1
    freq = M.flatten()
    h_ab=0
    for x in freq:
      if x:
        h_ab+=-x/total *log(x/total)
    mi = h_a + h_b - h_ab
    return mi
    ''' 
    b.reverse()
    a=np.array(a)
    b = np.array(b)
    c= np.minimum(a,b)
    freq=c.tolist()
    while len(c)>0:
        a=np.subtract(a,c)
        b = np.subtract(b, c)
        b=b.tolist()
        b.reverse()
        b=np.array(b)
        a = a[~(a == 0)]
        b = b[~(b == 0)]
        c = np.minimum(a, b)
        freq+=c.tolist()
    print(freq)
    '''


def get_piv_ct_table(data,x,y,z,fraction):
    # create a contingacy table and some statistics regarding mutual information
    grouped = data.groupby(z)
    sampledgroups=grouped.size().index
    size=len(data.index)
    columns = ['groupname', 'prob', 'xmargin', 'ymargin', 'wmi','bound']
    df = pd.DataFrame(columns=columns)
    if 1:
        ## create a group by object
        tmp=data.groupby(z+x).size()
        x_good_groups=tmp.groupby(z).size()
        tmp=data.groupby(z+y).size()
        y_good_groups=tmp.groupby(z).size()
        grouped = data.groupby(z)
        groupedsize = grouped.size()
        groupedname = groupedsize.index.values
        #print('orgi',len(groupedname))
        grouplist = groupedsize
        x_good_groups=np.subtract(x_good_groups,np.repeat(1, len(x_good_groups)))
        y_good_groups = np.subtract(y_good_groups, np.repeat(1, len(y_good_groups)))
        good_groups=np.multiply(x_good_groups, y_good_groups)
        grouplist=np.multiply(good_groups,grouplist)
        total=sum(grouplist)
        goodindex=np.nonzero(grouplist)
        sampledgroups=groupedsize.ix[goodindex]

        ## sample from the groups
        if fraction<1:
            weights=grouplist.ix[goodindex].values
            weights=weights  / np.sum(weights)
            gg=np.sum(weights)
            num=np.size(goodindex)
            print('xxxxx')
            print(num)
            if num==0:
                return df, size, 0
            if num<50:
                sampledgroups = sampledgroups.index.values
            else:
                if num < 100:
                    fraction = 1
                else:
                    fraction=1/num*fraction*200
                if num>5000:
                    fraction = 1 / num * fraction * 100
                if num>10000:
                    fraction = 1 / num * fraction /2
                if gg==1:
                   sampledgroups = sampledgroups.sample(frac=fraction, replace=False, weights=weights)
                elif gg!=0:
                   sampledgroups = sampledgroups.sample(frac=fraction, replace=False)
                else:
                    return df,size,0
                sampledgroups=sampledgroups.index.values
        else:
            sampledgroups = sampledgroups.index.values
            #print(sampledgroups)
    ## compute the original conditional mutual information
    stat_0 = 0
    #print('sampleorgi', len(sampledgroups))
    for name in sampledgroups:
        try:
         subgroup=grouped.get_group(name)
        except:
            continue
        groupsize = len(subgroup.index)
        x_margin = subgroup.groupby(x).size()
        y_margin = subgroup.groupby(y).size()
        if len(x_margin)>=2 and len(y_margin)>=2:   ### discard the group if it has zero entropy
            xy_margins = subgroup.groupby(x + y).size()
            prob = groupsize / size
            h_x=entropy(x_margin)
            h_y=entropy(y_margin)
            wmi = (h_x + h_y - entropy(xy_margins)) * prob
            bound=min(h_x,h_y)*prob
            df.loc[len(df)] = [name, prob, x_margin.values, y_margin.values, wmi,bound]
            stat_0 += wmi
    #print(len(df.index))
    return df,size,stat_0



def get_ct_table(data,x,y,z,fraction,maxmc,cont=False, debug=False):
    # create a contingacy table and some statistics regarding mutual information

    start=time.time()
    g_grouped = data.groupby(remove_dup(x+y+z))['count'].sum().reset_index(name = "count")
    #print(len(g_grouped))
    grouped =g_grouped.groupby(z)['count'].sum().reset_index(name = "count")
    groupsize=grouped['count']
    size=sum(g_grouped['count'])
    columns = ['groupname', 'prob', 'xmargin', 'ymargin', 'wmi','bound']
    df = pd.DataFrame(columns=columns)

    fre_xz=g_grouped.groupby(z+x)['count'].sum()
    x_good_groups=fre_xz.groupby(z).size()  ## compute groups with non-zere H(z|x)
    #x_good_groups = x_good_groups - 2
    #print(len(x_good_groups))
    fre_yz=g_grouped.groupby(z+y)['count'].sum()
    y_good_groups = fre_yz.groupby(z).size()

    fre_xyz = g_grouped.groupby(z+x + y)['count'].sum()
    high_good_groups = fre_xyz.groupby(z).size()
    y_good_groups = fre_yz.groupby(z).size()
    #y_good_groups = y_good_groups - 2
    #print(len(y_good_groups))
    good_groups=np.multiply(x_good_groups, y_good_groups)
    good_groups[good_groups > 0]=1
    fre_xy = g_grouped.groupby(x + y)['count'].sum()
    good_groups[good_groups <= 0] = 0
    #good_groups=np.min(x_good_groups, y_good_groups)
    good_groups = np.multiply(good_groups, high_good_groups)
    groupsize=np.multiply(good_groups,groupsize)
    sampledgroups=groupsize[groupsize>0]

    #sampledgroups=np.nonzero(groupsize)
    #sampledgroups=groupsize.ix[goodindex]

    ## sample from the groups
    num = np.size(sampledgroups)  # num of groups
    if debug:
        print('xxxxx')
        print(num)
    if num==0:
        return df, size, 0
    #print(maxmc)
    if fraction<1 and num>10:
                weights=sampledgroups  / np.sum(sampledgroups)
                n=log10(num)*log10(num)*20*fraction
                n=int(n)
                print(num)
                print(n)
                if n<50:
                    sampledgroups = sampledgroups.sample(n=min(num,50), replace=False, weights=weights)
                elif n >300:
                    sampledgroups = sampledgroups.sample(n=min(num, 300), replace=False, weights=weights)
                else:
                    sampledgroups = sampledgroups.sample(n=n, replace=False, weights=weights)
                sampledgroups = sampledgroups.index.values
                if debug:
                    print('xxxxx')
                    print(len(sampledgroups))
    else:
        sampledgroups = sampledgroups.index.values
            #print(sampledgroups)
    ## compute the original conditional mutual information
    end=time.time()
    stat_0 = 0
    #print('sampleorgi', len(sampledgroups))
    grouped = g_grouped.groupby(z)
    for name in sampledgroups:
        subgroup=grouped.get_group(name)
        groupsize = sum(subgroup['count'])
        x_margin = subgroup.groupby(x)['count'].sum()
        y_margin = subgroup.groupby(y)['count'].sum()
        if len(x_margin)>=2 and len(y_margin)>=2:   ### discard the group if it has zero entropy
            xy_margins = subgroup.groupby(x + y)['count'].sum()
            prob = groupsize / size
            h_x=entropy(x_margin)
            h_y=entropy(y_margin)
            wmi = (h_x + h_y - entropy(xy_margins)) * prob
            bound=min(h_x,h_y)*prob
            df.loc[len(df)] = [name, prob, x_margin.values, y_margin.values, wmi,bound]
            stat_0 += wmi
    return df,size,stat_0


def ulti_fast_permutation_tst(data, x, y ,z=[], ratio=0.5, pvalue=0.05, num_samples=5000, debug=False,
                              fraction=1, loc_num_samples=100, cont=False,view=True,maxmc=100,bin=100):
    ### covert input to list if ther are string

    if isinstance(x, str):
        x = [x]
    if isinstance(y, str):
        y = [y]
    if view==False:
        data = data.groupby(remove_dup(x+y+z)).size()
        data = pd.DataFrame(data.reset_index(name="count"))

    ## number of simulated permutation test taken for each group
    localsample=loc_num_samples
    if z:
        if isinstance(z, str):
            z = [z]
        #row_num=get_distinct(daxta,x)   ## compute frequency of x
        #col_num=get_distinct(data, y)  ## compute frequency of y

        df, size, stat_0=get_ct_table(data,x,y,z,fraction,cont=cont,debug=debug,maxmc=maxmc)   #create a k -way contingacy table
        #z_states=len(df.index)
        ''' 
        if fraction<-1 and z_states>1000000000:
            par_z_states = int(len(df.index) * fraction)
            df = df.sort_values(by='wmi', ascending=False)  # sort by the value of wmi
            df = df.reset_index(drop=True)
            resi=df.loc[par_z_states+1:z_states+1]
            df=df.loc[0:par_z_states]
            stat_0-=np.sum(resi['wmi'])
        '''
        #df=df.sort_values(by='wmi',ascending=False) #sort by the value of wmi
        #print(df)
        #if fraction!=1:
        #   #if len(df.index)>10000:
                #sampledgroups=data.groupby(z).apply(lambda x: x.sample(frac=.1))
        #    df=df.sample(frac=fraction, replace=False) #weights=pro
        #    if debug:
        #       print('samplegroup size')
        #       print(len(df.index))
        #print(df)
        #print(df)
        if debug:
          print(stat_0)
        per_margins=dict()
        counter = 0
        x=[]
        if len(df.index)>0:
            for index, row in df.iterrows():
                prob = row['prob']
                x_margins = row['xmargin']
                y_margins = row['ymargin']
                counter+=1
                ran_mi=generate_permuated_mi2(x_margins,y_margins,prob,loc_num_samples)
                #print(loc_num_samples)
                if loc_num_samples<num_samples:
                  base=choices(ran_mi, k=num_samples)
                else:
                  base=ran_mi
                for i in range(1,num_samples):
                  if i in  per_margins:
                     per_margins[i] +=base[i]
                  else:
                     per_margins[i] = base[i]

            k=0
            for key in per_margins.keys():
                cmi=np.sum(per_margins[key])
                x.insert(0,cmi)
                if cmi>=stat_0:
                    k += 1
        else:
            k=num_samples
    else:
        record=list()
        k=0
        x_margins = data.groupby(x)['count'].sum()
        y_margins = data.groupby(y)['count'].sum()
        if len(x_margins)<2 or len(y_margins)<2:
            return [1, 0]
        c = data.groupby(x+y)['count'].sum()
        h_a = entropy(x_margins)
        h_b = entropy(y_margins)
        h_ab = entropy(c)
        r2dtable = ro.r['r2dtable']
        R = ro.r
        stat_0 = h_a + h_b - h_ab
        x_margins = R('c' + str(tuple(x_margins)))
        y_margins = R('c' + str(tuple(y_margins)))
        if sum(x_margins)!= sum(y_margins):
            return [-1,-1]
        samples = r2dtable(localsample, x_margins, y_margins)
        k=0
        for sample in samples:
            freq = np.array(sample).flatten()
            mi = h_a + h_b - entropy(freq.tolist())
            record.insert(0, mi)
            # compute number of time that we get a permutation mi greater than the sample mutual information
            k += stat_0 <= mi
        x=record
    #for i in entropy_vector.values():
    #    if i>=stat_0:
    #      k+=1
    #print('sampling completed')
    #print(end - start)

    #print(indicator)
    if debug:
        print('original mutual', stat_0)
        plt.hist(x,bin)
        plt.show()
    pval = (1.0*k) / num_samples
    ci_low=pval-1.96 * sqrt(pval*(1-pval)/num_samples)
    ci_hight=pval+1.96 * sqrt(pval*(1-pval)/num_samples)
    if debug:
        print("#####")
        print(k)
        print((ci_low,ci_hight))
        print("#####")
    return [max(ci_hight, 1.0/num_samples),stat_0]

def ulti_fast_permutation_tst_cmi4(data, x, y, z=[], ratio=0.5, pvalue=0.05, num_samples=5000, debug=False,
                                    fraction=1, k=100, optimized=False):
    ### covert input to list if ther are string

    start = time.time()
    if isinstance(x, str):
        x = [x]
    if isinstance(y, str):
        y = [y]

    ## number of simulated permutation test taken for each group
    localsample=100
    start = time.time()



    if z:
        if isinstance(z, str):
            z = [z]
        ## size of data
        size=len(data.index)
        #row_num=get_distinct(data,x)   ## compute frequency of x
        #col_num=get_distinct(data, y)  ## compute frequency of y

        df, size, stat_0=get_ct_table(data,x,y,z,fraction,debug=debug)   #create a k -way contingacy table
        #df=df.sort_values(by='wmi',ascending=False) #sort by the value of wmi
        #print(df)
        #z_states=len(df.index)
        #if fraction<1 and z_states>10:
        #    par_z_states = int(len(df.index) * fraction)
        #    df = df.sort_values(by='wmi', ascending=False)  # sort by the value of wmi
        #    df = df.reset_index(drop=True)
        #    resi=df.loc[par_z_states+1:z_states+1]
        #    df=df.loc[0:par_z_states]
        #    stat_0-=np.sum(resi['wmi'])
        #print(df)
        df = df.sort_values(by='bound', ascending=False)  # sort by the value of wmi
        df=df.reset_index(drop=True)
        #print(df)

        partial_per_cmi=dict()    ## keeps partial cmi on permuted samples
        sample_cont_tables=dict()  ## keep permutation sample for each group
        indicator=dict()         ## dictionary of incicators which records the p-value of each permuated sample
        bound_dic = dict()
        if debug:
          print(stat_0)
        #print('initialization time')
        #print(end - start)
        res=list()  ## records the upper bounds

        ### compute the upper bound for the mutual information of each group times its probabality
        good_groups=list()
        redidual=0

        ''' 
        for index, row in df.iterrows():
            name = row['name']
            prob = row['prob']
            x_margins = row['xmargin']
            y_margins = row['ymargin']
            #print(a.values,b.values)
            bound=groupsize/size* get_max_mi(x_margins.values,y_margins.values)*1/fraction
              if bound!=0:
               res.insert(0,bound)
               good_groups.insert(0, name)
            else:
                h_a = entropy(x_margins)
                h_b = entropy(y_margins)
                y_margins = subgroup.groupby(y).size()
                h_ab = entropy(y_margins)
                redidual =redidual+ groupsize / size *(h_a+h_b-h_ab) * 1 / fraction
'''

        counter = 0
        sampleflags=np.arange(1, num_samples,1).tolist()
        upper_bound = sum(df['bound'])
        if len(df.index)>0:
            for index, row in df.iterrows():
                name = row['groupname']
                prob = row['prob']
                x_margins = row['xmargin']
                y_margins = row['ymargin']
                counter+=1
                ### check how manny p-values are computed
                ##p=len(indicator.keys())
                #print(p)
                if len(sampleflags)==0:  # checks if all permutaed samples are settled
                    #pass
                    break
                #print(len(sampleflags),index)
                check_ones=sum(indicator.values())  # checks if all we get enough evidance to rekect the null hypotheis
                if check_ones >= pvalue*num_samples:
                    #pass
                    break
                #print(len(sampleflags))
                #print(counter)
                #print(len(df.index))
                for i in sampleflags:
                   if i in partial_per_cmi.keys():
                       if partial_per_cmi[i] >= stat_0:
                           indicator[i]=1
                           sampleflags.remove(i)
                           continue
                       #print(counter)
                       if index>0:
                           bound= upper_bound+partial_per_cmi[i]
                           if bound<stat_0:
                               indicator[i] = 0
                               sampleflags.remove(i)
                               continue
                   if  name not in sample_cont_tables.keys():
                            ran_mi=generate_permuated_mi2(x_margins,y_margins,prob,localsample)
                            ran_mi=choices(ran_mi, k=num_samples)
                            sample_cont_tables[name]=ran_mi
                   else:
                       ran_mi=sample_cont_tables[name]
                       if i not in partial_per_cmi.keys():
                          if ran_mi==0:

                              partial_per_cmi[i]=0
                          else:

                              partial_per_cmi[i]= ran_mi[i]*1/fraction #randrange(0,localsample)
                       else:
                          if ran_mi==0:
                              partial_per_cmi[i]+=0
                          else:
                              tmp=partial_per_cmi[i]
                              partial_per_cmi[i]+=ran_mi[i]*1/fraction
                #print(upper_bound)
                upper_bound-=df['bound'][index]

            k = sum(list(indicator.values()))
            x = list(partial_per_cmi.values())
        else:
            k=num_samples
    else:
        record=list()
        k=0
        x_margins = data.groupby(x).size()
        y_margins = data.groupby(y).size()
        c = data.groupby(x + y).size()
        h_a = entropy(x_margins)
        h_b = entropy(y_margins)
        h_ab = entropy(c)
        r2dtable = ro.r['r2dtable']
        R = ro.r
        stat_0 = h_a + h_b - h_ab
        x_margins = R('c' + str(tuple(x_margins)))
        y_margins = R('c' + str(tuple(y_margins)))
        if sum(x_margins)!= sum(y_margins):
            return [-1,-1]
        samples = r2dtable(num_samples, x_margins, y_margins)
        for sample in samples:
            freq = np.array(sample).flatten()
            mi = h_a + h_b - entropy(freq.tolist())
            record.insert(0, mi)
            # compute number of time that we get a permutation mi greater than the sample mutual information
            k += stat_0 <= mi
        x=record
    #for i in entropy_vector.values():
    #    if i>=stat_0:
    #      k+=1
    #print('sampling completed')
    #print(end - start)

    #print(indicator)
    if debug:
        plt.hist(x)
        plt.show()
    pval = (1.0*k) / num_samples
    ci_low=pval-1.96 * sqrt(pval*(1-pval)/num_samples)
    ci_hight=pval+1.96 * sqrt(pval*(1-pval)/num_samples)
    if debug:
        print("#####")
        print(k)
        print((ci_low,ci_hight))
        print("#####")
    return [max(ci_hight, 1.0/num_samples),stat_0]




def smart_fast_permutation_tst_cmi4(data, x, y, z=[], ratio=0.5, pvalue=0.05, num_samples=5000, debug=False,
                                    fraction=1, optimized=False):
    ### covert input to list if ther are string

    start = time.time()
    if isinstance(x, str):
        x = [x]
    if isinstance(y, str):
        y = [y]

    ## number of simulated permutation test taken for each group
    localsample=100
    start = time.time()

    ## compute the original conditional mutual information
    stat_0=info.Info.CMI(data, x ,y, z)

    if z:
        if isinstance(z, str):
            z = [z]
        ## size of data
        size=len(data.index)
        #row_num=get_distinct(data,x)   ## compute frequency of x
        #col_num=get_distinct(data, y)  ## compute frequency of y
        grouped = data.groupby(z)      ## create a group by object

        groupedsize=grouped.size()     ## this is a tupel which contain group names  and group's dataframe

        ## sample from the group by object

        ####  a dataframe which contains group name and their frequencies  and sorted by the sizes
        df=pd.DataFrame({'group':groupedsize.index.values, 'size':groupedsize.values})
        print('number of groups')
        print(len(df.index))
        df=df[df['size']>2]
        print('number of groups')
        print(len(df.index))
        df=df.sort_values(by=['size'],ascending=False)
        end=time.time()
        print('initialization',end-start)
        ####
        if fraction!=1:
           if len(groupedsize)>10000:
                #sampledgroups=data.groupby(z).apply(lambda x: x.sample(frac=.1))
                groupedsize=groupedsize.sample(frac=fraction, replace=False) #weights=pro
           if debug:
               print('samplegroup size')
               print(len(groupedsize))

        ## list of group sizes
        grouplist=groupedsize.tolist()

        entropy_vector=dict()    ## keeps entropies
        sample_cont_tables=dict()  ## keep permutation sample for each group
        indicator=dict()         ## dictionary of incicators which records the p-value of each permuated sample
        if debug:
          print(stat_0)
        #print('initialization time')
        #print(end - start)
        res=list()  ## records the upper bounds

        ### compute the upper bound for the mutual information of each group times its probabality
        good_groups=list()
        redidual=0
        for name in df['group']:

            subgroup = grouped.get_group(name)
            groupsize = len(subgroup.index)
            a = subgroup.groupby(x).size()
            b = subgroup.groupby(y).size()
            #print(a.values,b.values)
            if  (len(a) >= 2 and len(b) >= 2) and groupsize>10:
              bound=groupsize/size* get_max_mi(a.values,b.values)*1/fraction
              if bound!=0:
               res.insert(0,bound)
               good_groups.insert(0, name)
            else:
                h_a = entropy(a)
                h_b = entropy(b)
                b = subgroup.groupby(y).size()
                h_ab = entropy(b)
                redidual =redidual+ groupsize / size *(h_a+h_b-h_ab) * 1 / fraction


        res.reverse()
        #print(len(df.index))
        df=df[df['group'].isin(good_groups)]
        #print(len(df.index))

        k=0
        ### compute the upper bound for the mutual information of each group times its probabality
        ### plues the upper bounds of the MI of smaller groups

        for i in range(0,len(res)):
            tmp=0
            for j in range(i, len(res)):
                tmp+= res[j]
            res[i]=tmp
        ###
        #print(res)
        counter = 0
        if len(df.index==0):
            for name in df['group']:
                counter+=1
                ### check how manny p-values are computed
                p=len(indicator.keys())
                #print(p)
                if p==num_samples-1:
                    break

                check_ones=sum(indicator.values())
                if check_ones >= pvalue*num_samples:
                    break
                #subgroup = grouped.get_group(name)
                groupsize = len(subgroup.index)
                #if groupsize<2:
                #    break
                #print(groupsize)
                for i in range(1, num_samples):
                   if i in entropy_vector.keys():
                       if entropy_vector[i] >= stat_0-redidual:
                           indicator[i]=1
                           #print(i,counter)
                           #continue
                       upper_bound=res[counter-1]+entropy_vector[i]
                       if upper_bound<stat_0:
                           indicator[i] = 0
                           continue
                   if  name not in sample_cont_tables.keys():
                            ran_mi=generate_permuated_mi(grouped,name,x,y,localsample,size,fraction)
                            sample_cont_tables[name]=ran_mi
                   else:
                       ran_mi=sample_cont_tables[name]
                   if i not in entropy_vector.keys():
                      if ran_mi==0:
                          entropy_vector[i]=0
                      else:
                          entropy_vector[i]= ran_mi[randrange(0,localsample)]
                   else:
                      if ran_mi==0:
                          entropy_vector[i]+=0
                      else:
                          entropy_vector[i]+=ran_mi[randrange(0,localsample)]
                #print(df[df.loc[df['group'].isin(name)]])

            k = sum(list(indicator.values()))
            x = list(entropy_vector.values())
        else:
            k=num_samples
    else:
        record=list()
        k=0
        a = data.groupby(x).size()
        b = data.groupby(y).size()
        c = data.groupby(x + y).size()
        h_a = entropy(a)
        h_b = entropy(b)
        h_ab = entropy(c)
        r2dtable = ro.r['r2dtable']
        R = ro.r
        stat_0 = h_a + h_b - h_ab
        a = R('c' + str(tuple(a)))
        b = R('c' + str(tuple(b)))
        if sum(a)!= sum(b):
            return [-1,-1]
        samples = r2dtable(num_samples, a, b)
        for sample in samples:
            freq = np.array(sample).flatten()
            mi = h_a + h_b - entropy(freq.tolist())
            record.insert(0, mi)
            # compute number of time that we get a permutation mi greater than the sample mutual information
            k += stat_0 <= mi
        x=record
    #for i in entropy_vector.values():
    #    if i>=stat_0:
    #      k+=1
    #print('sampling completed')
    #print(end - start)

    #print(indicator)
    if debug:
        plt.hist(x)
        plt.show()
    pval = (1.0*k) / num_samples
    ci_low=pval-1.96 * sqrt(pval*(1-pval)/num_samples)
    ci_hight=pval+1.96 * sqrt(pval*(1-pval)/num_samples)
    if 1:
        print("#####")
        print(k)
        print((ci_low,ci_hight))
        print("#####")
    return [max(ci_hight, 1.0/num_samples),stat_0]

    '''  
        record=np.array()
        end = time.time()
        print('time')
        print(end - start)
        for i in range(0, num_samples):
            cmi=residual
            for item in res.keys():
                cmi+=res[item][random.randint(0, localsample-1)]
            np.insert(record, cmi)
            # compute number of time that we get a permutation mi greater than the sample mutual information
            k += stat_0 <= cmi
    else:
        a = data.groupby(x).size()
        b = data.groupby(y).size()
        c= data.groupby(x+y).size()
        h_a=entropy(a)
        h_b=entropy(b)
        h_ab = entropy(c)
        stat_0=h_a+h_b-h_ab
        a=R('c'+str(tuple(a)))
        b=R('c' + str(tuple(b)))
        samples=r2dtable(num_samples,a,b)
        for sample in samples:
            freq=np.array(sample).flatten()
            mi = h_a+h_b-entropy(freq.tolist())
            record.insert(0, mi)
            # compute number of time that we get a permutation mi greater than the sample mutual information
            k += stat_0 <= mi
    if debug:
        print(x)
        print(y)
        print(z)
        print(stat_0)
        print(k)
        plt.hist(record)
        plt.show()
        #time.sleep(1)
        #plt.close()

    pval = (1.0*k) / num_samples
    ci_low=pval-1.96 * sqrt(pval*(1-pval)/num_samples)
    ci_hight=pval+1.96 * sqrt(pval*(1-pval)/num_samples)
    print("#####")
    print(k)
    print((ci_low,ci_hight))
    print("#####")
    return [max(ci_hight, 1.0/num_samples),stat_0]
'''


def fast_permutation_tst_cmi3(data, x, y, z=[], ratio=0.5, pvalue=0.05, num_samples=5000, debug=False,
                              fraction=1,optimized=False):
    if isinstance(x, str):
        x = [x]
    if isinstance(y, str):
        y = [y]
    Rstats = importr('stats')
    r2dtable = ro.r['r2dtable']
    R = ro.r
    record = []
    k = 0
    localsample=100
    start = time.time()
    inf=info.Info(data)
    stat_0=inf.CMI(x ,y, z)
    if z:
        if isinstance(z, str):
            z = [z for z in z.split(",")]
        res=dict()
        size=len(data.index)
        grouped = data.groupby(z)
        groupedsize=grouped.size()
        groupedname = groupedsize.index.values
        grouplist=groupedsize.tolist()
        pro=list()
        total=len(grouplist)
        inclutiondic=dict()
        frac = fraction
        for item in grouplist:
            pro.insert(0, item / total)
            #print(item / total)
        pro.reverse()
        #prob=0 #groupedsize.tolist()/len(groupedsize.tolist())
        sampledgroups = groupedsize
        if debug:
         print('group size')
        print(len(groupedsize))
        if fraction!=1:
           if len(groupedname)>100:
                #sampledgroups=data.groupby(z).apply(lambda x: x.sample(frac=.1))
                sampledgroups=groupedsize.sample(n=int(frac*total), replace=False) #weights=pro
           if debug:
               print('samplegroup size')
               print(len(sampledgroups))
        else:
            pass
            #sampledgroups=groupedsize
            #sampledgroups=np.random.choice(groupedname, 100,replace=False,p=pro)
            #print('########################')
            #print(sum(pro)*total)
            #print(len(groupedsize.index.values))
            #print(len(sampledgroups.index.values))
            #print('########################')
            #for groups in np.nditer(sampledgroups):
            #  print(groups)

        i=0
        residual=0
        for name in sampledgroups.index.values:
             tmp=sampledgroups[name]
             inclusion=fraction# (tmp/total)
             subgroup=grouped.get_group(name)
             groupsize = len(subgroup.index)
             a=subgroup.groupby(x).size()
             b = subgroup.groupby(y).size()
             if not len(a)>=2 or not len(b)>=2:
                 #h_a = entropy(a)
                 #h_b = entropy(b)
                 #c = subgroup.groupby(x+y).size()
                 #residual+=((h_a+h_b-entropy(c))*groupsize/size)/inclusion
                 continue
             a = R('c' + str(tuple(a)))
             b = R('c' + str(tuple(b)))
             h_a = entropy(a)
             h_b = entropy(b)
             #print('table generation')
             start = time.time()
             if sum(a)==sum(b):
                    samples = r2dtable(localsample, a, b)
             end = time.time()
             #print('time')
             #print(end - start)
             #print('table generated')
             i+=1
             sys.stdout.write("Permuted samples ... %s%%\r" % (i*100/len(grouped)))
             sys.stdout.flush()
             record=[]
             for sample in samples:
                 freq = np.array(sample).flatten()
                 groupsize1 = freq.sum()
                 #print(inclusion)
                 mi_z = ((h_a+h_b-entropy(freq.tolist()))*groupsize/size)/inclusion
                 record.insert(0,mi_z)
             res[name]=record
        #print(i)
        record=[]
        end = time.time()
        #print('time')
        #print(end - start)
        for i in range(0, num_samples):
            cmi=residual
            for item in res.keys():
                cmi+=res[item][random.randint(0, localsample-1)]
            record.insert(0, cmi)
            # compute number of time that we get a permutation mi greater than the sample mutual information
            k += stat_0 <= cmi
    else:
        a = data.groupby(x).size()
        b = data.groupby(y).size()
        c= data.groupby(x+y).size()
        h_a=entropy(a)
        h_b=entropy(b)
        h_ab = entropy(c)
        stat_0=h_a+h_b-h_ab
        a=R('c'+str(tuple(a)))
        b=R('c' + str(tuple(b)))
        samples=r2dtable(num_samples,a,b)
        for sample in samples:
            freq=np.array(sample).flatten()
            mi = h_a+h_b-entropy(freq.tolist())
            record.insert(0, mi)
            # compute number of time that we get a permutation mi greater than the sample mutual information
            k += stat_0 <= mi
    if debug:
        print(x)
        print(y)
        print(z)
        print(stat_0)
        print(k)
        plt.hist(record)
        plt.show()
        #time.sleep(1)
        #plt.close()

    pval = (1.0*k) / num_samples
    ci_low=pval-1.96 * sqrt(pval*(1-pval)/num_samples)
    ci_hight=pval+1.96 * sqrt(pval*(1-pval)/num_samples)
    print("#####")
    print(k)
    print((ci_low,ci_hight))
    print("#####")
    return [max(ci_hight, 1.0/num_samples),stat_0]




def fast_permutation_tst_cmi4(data, x, y, z=[], ratio=0.5, pvalue=0.05, num_samples=5000, debug=False,
                              fraction=1,optimized=False):
    if isinstance(x, str):
        x = [x]
    if isinstance(y, str):
        y = [y]
    Rstats = importr('stats')
    r2dtable = ro.r['r2dtable']
    R = ro.r
    record = []
    k = 0
    localsample=100
    start = time.time()
    stat_0=info.Info.CMI(data, x ,y, z)
    if z:
        if isinstance(z, str):
            z = [z for z in z.split(",")]
        res=dict()
        size=len(data.index)
        grouped = data.groupby(z)
        groupedsize=grouped.size()
        groupedname = groupedsize.index.values
        grouplist=groupedsize.tolist()
        pro=list()
        total=len(grouplist)
        inclutiondic=dict()
        frac = fraction
        for item in grouplist:
            pro.insert(0, item / total)
            #print(item / total)
        pro.reverse()
        #prob=0 #groupedsize.tolist()/len(groupedsize.tolist())
        sampledgroups = groupedsize
        if debug:
         print('group size')
        print(len(groupedsize))
        if fraction!=1:
           if len(groupedname)>100:
                #sampledgroups=data.groupby(z).apply(lambda x: x.sample(frac=.1))
                sampledgroups=groupedsize.sample(n=int(frac*total), replace=False) #weights=pro
           if debug:
               print('samplegroup size')
               print(len(sampledgroups))
        else:
            pass
            #sampledgroups=groupedsize
            #sampledgroups=np.random.choice(groupedname, 100,replace=False,p=pro)
            #print('########################')
            #print(sum(pro)*total)
            #print(len(groupedsize.index.values))
            #print(len(sampledgroups.index.values))
            #print('########################')
            #for groups in np.nditer(sampledgroups):
            #  print(groups)

        i=0
        residual=0
        for name in sampledgroups.index.values:
             tmp=sampledgroups[name]
             inclusion=fraction# (tmp/total)
             subgroup=grouped.get_group(name)
             groupsize = len(subgroup.index)
             a=subgroup.groupby(x).size()
             b = subgroup.groupby(y).size()
             if not len(a)>=2 or not len(b)>=2:
                 #h_a = entropy(a)
                 #h_b = entropy(b)
                 #c = subgroup.groupby(x+y).size()
                 #residual+=((h_a+h_b-entropy(c))*groupsize/size)/inclusion
                 continue
             a = R('c' + str(tuple(a)))
             b = R('c' + str(tuple(b)))
             h_a = entropy(a)
             h_b = entropy(b)
             #print('table generation')
             start = time.time()
             if sum(a)==sum(b):
                    samples = r2dtable(localsample, a, b)
             end = time.time()
             #print('time')
             #print(end - start)
             #print('table generated')
             i+=1
             sys.stdout.write("Permuted samples ... %s%%\r" % (i*100/len(grouped)))
             sys.stdout.flush()
             record=[]
             for sample in samples:
                 freq = np.array(sample).flatten()
                 groupsize1 = freq.sum()
                 #print(inclusion)
                 mi_z = ((h_a+h_b-entropy(freq.tolist()))*groupsize/size)/inclusion
                 record.insert(0,mi_z)
             res[name]=record
        #print(i)
        record=[]
        end = time.time()
        #print('time')
        #print(end - start)
        for i in range(0, num_samples):
            cmi=residual
            for item in res.keys():
                cmi+=res[item][random.randint(0, localsample-1)]
            record.insert(0, cmi)
            # compute number of time that we get a permutation mi greater than the sample mutual information
            k += stat_0 <= cmi
    else:
        a = data.groupby(x).size()
        b = data.groupby(y).size()
        c= data.groupby(x+y).size()
        h_a=entropy(a)
        h_b=entropy(b)
        h_ab = entropy(c)
        stat_0=h_a+h_b-h_ab
        a=R('c'+str(tuple(a)))
        b=R('c' + str(tuple(b)))
        samples=r2dtable(num_samples,a,b)
        for sample in samples:
            freq=np.array(sample).flatten()
            mi = h_a+h_b-entropy(freq.tolist())
            record.insert(0, mi)
            # compute number of time that we get a permutation mi greater than the sample mutual information
            k += stat_0 <= mi
    if debug:
        print(x)
        print(y)
        print(z)
        print(stat_0)
        print(k)
        plt.hist(record)
        plt.show()
        #time.sleep(1)
        #plt.close()

    pval = (1.0*k) / num_samples
    ci_low=pval-1.96 * sqrt(pval*(1-pval)/num_samples)
    ci_hight=pval+1.96 * sqrt(pval*(1-pval)/num_samples)
    print("#####")
    print(k)
    print((ci_low,ci_hight))
    print("#####")
    return [max(ci_hight, 1.0/num_samples),stat_0]


def perf(a,b,num_samples):
    Rstats = importr('stats')
    r2dtable = ro.r['r2dtable']
    R = ro.r
    a = R('c' + str(tuple(a)))
    b = R('c' + str(tuple(b)))
    exp=list()
    record=list()
    for i in range(100, num_samples,10000):
        print(i)
        start = time.time()
        samples = r2dtable(10000, a, b)
        end = time.time()
        record.insert(0, end-start)
        print(end-start)
    record.reverse()
    plt.plot(record)
    plt.show()


def fast_permutation_tst_cmi(data, x, y, z=[], ratio=0.5, pvalue=0.05, num_samples=100, debug=False, optimized=False):
    Rstats = importr('stats')
    r2dtable = ro.r['r2dtable']
    R = ro.r
    stat_0=0
    record = []
    k = 0
    residual=0
    stat_0 = info.Info.CMI(data, x, y, z)
    i=0
    if z:
        res=dict()
        size=len(data.index)
        grouped = data.groupby(z)
        perf=list()
        for name, subgroup in grouped:
             groupsize = len(subgroup.index)
             a=subgroup.groupby(x).size()
             b = subgroup.groupby(y).size()
             if  len(a)>=2 and len(b)>=2:
                 a = R('c' + str(tuple(a)))
                 b = R('c' + str(tuple(b)))
                 print(a)
                 print(b)
                 h_a = entropy(a)
                 h_b = entropy(b)
                 #print('table generation')
                 start = time.time()
                 samples = r2dtable(num_samples, a, b)
                 end = time.time()
                 perf.insert(0,end)
                 #print('time')
                 #print(end - start)
                 #print('table generated')
                 record=[]
                 for sample in samples:
                     freq = np.array(sample).flatten()
                     groupsize1 = freq.sum()
                     mi_z = (h_a+h_b-entropy(freq.tolist()))*groupsize/size
                     record.insert(0,mi_z)
                     res[name]=record
             else:
                 h_a = entropy(a)
                 h_b = entropy(b)
                 h_ab = entropy(subgroup.groupby(x+y).size())
                 residual+=h_a+h_b-h_ab
        #print(res)
             i+=1
             sys.stdout.write("Permuted samples ... %s%%\r" % (i*100/len(grouped)))
             sys.stdout.flush()

        record=[]
        for i in range(0, num_samples):
            cmi=residual
            for item in res.keys():
                cmi+=res[item][i]
            record.insert(0, cmi)
            # compute number of time that we get a permutation mi greater than the sample mutual information
            k += stat_0 <= cmi
    else:
        a = data.groupby(x).size()
        b = data.groupby(y).size()
        c= data.groupby(x+y).size()
        h_a=entropy(a)
        h_b=entropy(b)
        h_ab = entropy(c)
        stat_0=h_a+h_b-h_ab
        a=R('c'+str(tuple(a)))
        b=R('c' + str(tuple(b)))
        samples=r2dtable(num_samples,a,b)
        for sample in samples:
            freq=np.array(sample).flatten()
            mi = h_a+h_b-entropy(freq.tolist())
            record.insert(0, mi)
            # compute number of time that we get a permutation mi greater than the sample mutual information
            k += stat_0 <= mi
    if debug:
        print(x)
        print(y)
        print(z)
        print(stat_0)
        print(k)
        plt.hist(record)
        plt.show()
        #time.sleep(1)
        #plt.close()

    pval = (1.0*k) / num_samples
    ci_low=pval-1.96 * sqrt(pval*(1-pval)/num_samples)
    ci_hight=pval+1.96 * sqrt(pval*(1-pval)/num_samples)
    print("#####")
    print((ci_low,ci_hight))
    print("#####")
    return [max(ci_hight, 1.0/num_samples),stat_0]


def permutation_tst_cmi(data, x, y, z=[], ratio=0.5, pvalue=0.05, num_samples=100, debug=False, optimized=False):
    if ratio<1:
     data = data.sample(frac=ratio, replace=False)

   # stat_0 = info.Info.CMI(data,x,y,z)
    if isinstance(x, str):
        x = [x]
    if isinstance(y, str):
        y = [y]
    if z:
        if isinstance(z, str):
            z = [z for z in z.split(",")]
        a = entropy(x + z)
        b = info.Info.entropy(tuple(y + z))
        if a != 0 and b != 0:
            c = info.Info.entropy(tuple(x + y + z))
            d = info.Info.entropy(tuple(z))
            stat_0 = (a + b - c - d)

        else:
         stat_0 = 0
    else:
        a = info.Info.entropy(tuple(x) )
        b = info.Info.entropy(tuple(y) )
        if a != 0 and b != 0:
            c = info.Info.entropy(tuple(x + y))
            stat_0 = a + b - c
        else:
         stat_0 = 0
    stat_1 = info.Info.CMI(x, y, z)
    record=[]
    cutoff=pvalue*num_samples
    k = 0
    i=0
    for _ in range(num_samples):
        permutation=data.copy()

        if z:
            groups=permutation.groupby(z)[x[0]]
            permutation=shuffle(permutation, x,z,groups)
        else:
            permutation = shuffle(permutation, x)
        c=info.Info.H(permutation, x + y+z)
        #print(info.Info.H(permutation, z))
        if z:
            mi=(a + b - c - d)
        else:
            mi = (a + b- c)
        #mi = info.Info.CMI(permutation, x, y, z)
        record.insert(0,mi)
        # compute number of time that we get a permutation mi greater than the sample mutual information
        k += stat_0 <= mi
        if optimized:
            if k>cutoff:
                break
            if num_samples-i<cutoff-k:
                break
        i+=1
        sys.stdout.write("Permuted samples ... %s%%\r" % (i*100/num_samples))
        sys.stdout.flush()
        #time.sleep(1)
        #print("\r")
        #sys.stdout.write('ddd')
        print(i)

    if debug:
        print(x)
        print(y)
        print(z)
        print(stat_0)
        print(k)
        print(i)
        plt.hist(record)
        plt.show()
        #time.sleep(1)
        #plt.close()

    pval = (1.0*k) / num_samples
    ci_low=pval-1.96 * sqrt(pval*(1-pval)/num_samples)
    ci_hight=pval+1.96 * sqrt(pval*(1-pval)/num_samples)
    print("#####")
    print(k)
    print((ci_low,ci_hight))
    print("#####")
    return [max(ci_hight, 1.0/num_samples),stat_0]




if __name__ == "__main__":
    #array=np.array([1,2,3,4,5])
    #X=bootstrap_ci_ct(array,np.mean)
    #print(X)

    #X = CIT(data, ['race'], ['income'], normilized=False)
    #print(X)
    #data = read_from_csv('/Users/babakmac/Documents/XDBData/paperexample2.csv')
    cov = ['capitalloss', 'hoursperweek', 'capitalgain', 'age', 'occupation', 'maritalstatus']
    #cov = ['capitalloss','hoursperweek']
    # test shuffle #########################
    #data = np.array([['', 'x', 'y'],
    #                 ['Row1', 'a', 2],
    #                 ['Row2', 'b', 2],['Row3', 'c', 2],['Row4', 1, 4],['Row5', 2, 4],['Row6', 3, 4]])

    #data=pd.DataFrame(data=data[1:, 1:],  # values
    #index = data[1:, 0],  # 1st column as index
    #columns = data[0, 1:])  # 1st row as the column names
    #print(data)
    #print(shuffle(data,['x'],['y']))
    #cov = ['race', 'capitalloss', 'workclass', 'hoursperweek', 'capitalgain', 'age', 'occupation', 'education', 'maritalstatus']
    #cov=['occupation']
    #print(data['occupation'].describe())
    start = time.time()
    #cov=['race', 'capitalloss', 'hoursperweek', 'capitalgain', 'income', 'maritalstatus']
    cov=[ 'deptime', 'arrtime', 'arrdelay','yyear']
    #x =permutation_tst_cmi(data, ['sex'],['income'],['hoursperweek'],
    #                             ratio=1, pvalue=0.05, num_samples=5000,
    #                             debug=True, optimized=False)
    #cov=['dayofweek']
    data = read_from_csv('/Users/babakmac/Documents/XDBData/berkeley.csv')
    print(data.columns)
    #data.drop(data.columns[[0]], axis=1, inplace=True)  ## drop the first column
    #data.columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    #data=data.groupby(['1', '4',  '9']).size()
    #data=pd.DataFrame(data.reset_index(name="count"))
    ulti_fast_permutation_tst(data, ['gender'], ['accepted'], ['department'],
                              ratio=1, pvalue=1, num_samples=1000,loc_num_samples=1000, fraction=1,
                              debug=True,view=False,bin=100)
    #permutation_tst_cmi(data, ['4'], ['9'], ['1'],
    #                ratio=1, pvalue=1, num_samples=1000,
    #                debug=True)

    end = time.time()
    print('time2222222')
    print(end - start)
    #perf([100,250], [150,200], 100000)
    #print(x)
    #['race', 'capitalloss', 'workclass', 'hoursperweek', 'capitalgain', 'age', 'occupation', 'education', 'maritalstatus', 'sex']
    #parents
    #[]

''' 
710
(0.68187553662734168, 0.73812446337265825)
#####
I: 0.059029910257
p-value: 0.738124463373
Boundary: ['monthh', 'yyear', 'crsdeptime', 'origin', 'dest', 'deptime', 'arrtime', 'arrdelay']
['delayed'],dayofmonth|['monthh', 'yyear', 'crsdeptime', 'origin', 'dest', 'deptime', 'arrtime', 'arrdelay']


Boundary: ['origin', 'dest', 'deptime', 'arrtime', 'arrdelay']
['delayed'],carrier|['origin', 'dest', 'deptime', 'arrtime', 'arrdelay']
#####
643
(0.61330415649286929, 0.67269584350713074)
#####
I: 0.000237784492869
p-value: 0.672695843507
Boundary: ['origin', 'dest', 'deptime', 'arrtime', 'arrdelay']
['delayed'],crsdeptime|['origin', 'dest', 'deptime', 'arrtime', 'arrdelay']

Boundary: ['arrdelay', 'arrtime', 'deptime', 'origin', 'crsdeptime']
time taken
90.5915892124176

Boundary: ['arrdelay', 'arrtime', 'deptime', 'monthh', 'origin', 'destcityname']
time taken
82.926353931427

Boundary: ['arrdelay', 'arrtime', 'deptime', 'destcityname']
time taken
45.7897891998291
'''
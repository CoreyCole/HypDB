
from FairDB.core.explanation import *
from statistics import mean

def SimposonReversal(data, treatment, outcome,cov):
    reversal = dict()
    exact=0
    for cv in cov:
        x = Check_Simpson(data, treatment, outcome,cv)
        if x:
            reversal[cv] = x
        if x==1:
            exact+1
    vls=list(reversal.values())
    return exact,mean(vls),reversal

def Check_Simpson(df, treatment,outcome, cv):
    res1 = pd.DataFrame({'ATE': df.groupby(treatment[0])[outcome[0]].mean()}).reset_index()
    treatstates = np.unique(res1[treatment])
    winer = treatstates[1]
    a = res1[res1[treatment[0]] == treatstates[0]]
    b = res1[res1[treatment[0]] == treatstates[1]]
    e = a['ATE'].values
    f = b['ATE'].values
    if e > f:
        winer = treatstates[0]
    res2 = pd.DataFrame(
        {'ATE': df.groupby([treatment[0] , cv])[outcome[0]].mean()}).reset_index()
    covstates = np.unique(df[cv])
    flag = 0
    for c in covstates:
            x = res2[res2[cv] == c]
            t1 = x[x[treatment[0]] == treatstates[0]]
            t2 = x[x[treatment[0]] == treatstates[1]]
            if t1['ATE'].values > t2['ATE'].values and winer == treatstates[1]:
                flag = flag + 1
            elif t1['ATE'].values < t2['ATE'].values and winer == treatstates[0]:
                flag = flag + 1
    return flag / len(covstates)

if __name__ == '__main__':
    ''' 
    data=read_from_csv('/Users/babakmac/Documents/XDBData/paperexample2.csv')
    x=naive_groupby(data,['carrier'], ['delayed'])
    print(x)
    cov = ['crsdeptime', 'yyear','deptime','arrdelay','origin']
    orderedcov=get_respon(data, ['carrier'], ['delayed'], cov)
    print(orderedcov)
    matched,adj_set=matching(data,['carrier'], ['delayed'],orderedcov,threshould=100)
    ratio, matcheddata, n1, n2, counts=matched
    x=adjusted_groupby(matcheddata,['carrier'], ['delayed'],adj_set)
    print(x)
    #NMI=info.Info.CMI(data,['carrier'], ['delayed'],adj_set,normilized=True)
    #print(NMI)
    '''
    treatment=['sex']
    outcome=['income']
    cov=['age', 'education', 'maritalstatus', 'occupation', 'race', 'capitalgain',
         'capitalloss', 'hoursperweek','nativecountry']
    #cov=['maritalstatus']
    data = read_from_csv('/Users/babakmac/Documents/XDBData/binadult.csv')
    x = SimposonReversal(data, treatment, outcome,cov)
    print(x)


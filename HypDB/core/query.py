

from hypdb.utils.read_data import *
from hypdb.core.matching import matching
from hypdb.utils.util import *
from pylab import *
import json
import numpy

def naive_groupby(data,treatment,outcome,where=[]):
    ate = data.sort_values(by=treatment).groupby(treatment)[outcome].mean().reset_index()
    return ate

def remove_dup(lst):
    lst=set(lst)
    return list(lst)

# mediatpor and init not needed for total effect
def adjusted_groupby(data,treatment,outcome,covariates,mediatpor=[],init=[],threshould=0):
    print(treatment,outcome,covariates,mediatpor,init)
    #print(data)
    #print(list(data.columns.values))
    #print(covariates)
    matcheddata ,adj_set,pur=matching(data, treatment, outcome, remove_dup(covariates+mediatpor), threshould=threshould)
    size = len(matcheddata.index)
    if mediatpor:
       tmp = matcheddata[matcheddata[treatment[0]].isin(init)]
       prob1 = pd.DataFrame({'prob1': tmp.groupby(remove_dup(mediatpor+covariates)).size() / size}).reset_index()
       #print(prob1)
    if covariates:
       prob2 = pd.DataFrame({'prob2': matcheddata.groupby(covariates).size() / size}).reset_index()
       #print(prob2)
    counts = pd.DataFrame({'count': matcheddata.groupby(treatment).size()}).reset_index()
    #print(counts)
    covariates.insert(0,treatment[0])
    #print(covariates)
    #print(list(data.columns.values))
    ate = data.groupby(remove_dup(mediatpor+covariates))[outcome].mean().reset_index()
    #print(ate)
    ate.rename(columns={outcome[0]: 'ATE_X'}, inplace=True)
    covariates.remove(treatment[0])
    if covariates and not mediatpor:
        ate = ate.merge(prob2, on=covariates)
        W_ATEX = ate['ATE_X']  * ate['prob2']
    if mediatpor and covariates:
        ate = ate.merge(prob2, on=covariates)
        ate = ate.merge(prob1, on=mediatpor)
        W_ATEX = ate['ATE_X'] * ate['prob1'] * ate['prob2']
    if mediatpor and not covariates:
        ate = ate.merge(prob1, on=mediatpor)
        W_ATEX = ate['ATE_X'] * ate['prob1']
    ate['WATE_X'] = W_ATEX
    wate = pd.DataFrame({outcome[0]: ate.groupby(treatment).sum()['WATE_X']}).reset_index()
    ate = wate.merge(counts, on=treatment, how='inner')
    return ate,matcheddata ,adj_set,pur

def plot(res,treatment,outcome,ylable='',title='',fontsize=10):
    outJSON = []
    outcomes = res[outcome[0]].values
    attrs = [[] for index in range(len(outcomes))]
    for i in range(len(outcomes)):
        for j in range(len(treatment)):
            attrs[i].append(res[treatment[j]].values[i])
    for i, j in zip(attrs, outcomes):
        temp = {}
        for k in range(len(treatment)):
            if type(i[k]).__module__ == 'numpy':
                temp[treatment[k]] = float(i[k])
            else:    
                temp[treatment[k]] = i[k]
        if type(i[k]).__module__ == 'numpy':
            temp[outcome[0]] = float(j)
        else:
            temp[outcome[0]] = j
        outJSON.append(temp)
    #print(outJSON)
    #print(json.dumps(outJSON))
    return outJSON

"""
par1 parents of the treatments
cov1 boundary of the treatments
par2 parents of the outcome
cov2 boundary of the outcome
"""
def graph(cov1, par1, cov2, par2, treatment, outcome, outJSON):
    outJSON['graph'] = {'nodes': [], 'links': [], 'correlation': {'dashed': True, 'treatment': treatment, 'outcome': outcome}}
    # in boundary of each other
    if treatment[0] in par2:
        outJSON['graph']['correlation']['dashed'] = False

    # edge doesn't exist but we need it for the graph
    if not outcome[0] in cov1 and not treatment[0] in cov2:
        outJSON['graph']['links'].append({'source': treatment[0], 'target': outcome[0]})
    # nodes
    for node in set(cov1 + cov2 + treatment + outcome):
        outJSON['graph']['nodes'].append({'id': node, 'label': node})
    # directed
    for node in par1:
        outJSON['graph']['links'].append({'source': node, 'target': treatment[0]})
        #print('par1', node, treatment[0])
    for node in par2:
        outJSON['graph']['links'].append({'source': node, 'target': outcome[0]})
        #print('par2', node, outcome[0])
    # undirected
    for node in set(cov1) - set(par1):
        outJSON['graph']['links'].append({'source': treatment[0], 'target': node})
        #print('cov1', node, treatment[0])
    for node in set(cov2) - set(par2):
        outJSON['graph']['links'].append({'source': outcome[0], 'target': node})
        #print('cov2', node, outcome[0])

    outJSON['graph']['links'] = [dict(t) for t in {tuple(d.items()) for d in outJSON['graph']['links']}]

    #print(outJSON['graph']['links'])

    #print(json.dumps(outJSON))

    # outJSON['graph']['treatment']['attributes'] = treatment
    # outJSON['graph']['treatment']['boundary'] = cov1
    # outJSON['graph']['treatment']['parents'] = par1
    # outJSON['graph']['outcome']['attributes'] = outcome
    # outJSON['graph']['outcome']['boundary'] = cov2
    # outJSON['graph']['outcome']['parents'] = par2

def grouped_bar(df):
    pos = list(range(len(df['pre_score'])))
    width = 0.25

    # Plotting the bars
    fig, ax = plt.subplots(figsize=(10, 5))

    # Create a bar with pre_score data,
    # in position pos,
    plt.bar(pos,
            # using df['pre_score'] data,
            df['pre_score'],
            # of width
            width,
            # with alpha 0.5
            alpha=0.5,
            # with color
            color='#EE3224',
            # with label the first value in first_name
            label=df['first_name'][0])

    # Create a bar with mid_score data,
    # in position pos + some width buffer,
    plt.bar([p + width for p in pos],
            # using df['mid_score'] data,
            df['mid_score'],
            # of width
            width,
            # with alpha 0.5
            alpha=0.5,
            # with color
            color='#F78F1E',
            # with label the second value in first_name
            label=df['first_name'][1])

    # Create a bar with post_score data,
    # in position pos + some width buffer,
    plt.bar([p + width * 2 for p in pos],
            # using df['post_score'] data,
            df['post_score'],
            # of width
            width,
            # with alpha 0.5
            alpha=0.5,
            # with color
            color='#FFC222',
            # with label the third value in first_name
            label=df['first_name'][2])

    # Set the y axis label
    ax.set_ylabel('Score')

    # Set the chart's title
    ax.set_title('Test Subject Scores')

    # Set the position of the x ticks
    ax.set_xticks([p + 1.5 * width for p in pos])

    # Set the labels for the x ticks
    ax.set_xticklabels(df['first_name'])

    # Setting the x-axis and y-axis limits
    plt.xlim(min(pos) - width, max(pos) + width * 4)
    plt.ylim([0, max(df['pre_score'] + df['mid_score'] + df['post_score'])])

    # Adding the legend and showing the plot
    plt.legend(['Pre Score', 'Mid Score', 'Post Score'], loc='upper left')
    plt.grid()
    plt.show()


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
    treatment=['sex']
    outcome=['income']
    cov=['age', 'education', 'maritalstatus', 'occupation', 'race', 'capitalgain',
         'capitalloss', 'hoursperweek','nativecountry']
    #cov=['maritalstatus']
    data = read_from_csv('/Users/babakmac/Documents/XDBData/binadult.csv')
    x = naive_groupby(data, treatment, outcome)
    print(x)
    orderedcov = get_respon(data, treatment, outcome, cov)
    print(orderedcov)
    matched, adj_set = matching(data, treatment, outcome, orderedcov, threshould=100)
    ratio, matcheddata, n1, n2, counts = matched
    x = adjusted_groupby(matcheddata, treatment, outcome, adj_set)
    print(x)
'''
    #data = read_from_csv('/Users/babakmac/Documents/XDBData/binadult.csv')
    data = read_from_db('qexpriment1037')
    treatment = ['carrier']
    outcome = ['delayed']
    cov1=['dest', 'origin', 'yyear', 'crsdeptime', 'month']
    cov2=['arrdelay', 'yyear', 'crsdeptime']
    x = naive_groupby(data, treatment, outcome)
    print(x)
    ate, matcheddata, adj_set, pur = adjusted_groupby(data, treatment, outcome,
                                                          covariates=['origin', 'yyear', 'month'],
                                                          mediatpor=[], init=[], threshould=90)
    print(ate)
    #plot(ate,treatment,outcome,'idadf','asffa')

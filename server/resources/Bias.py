from os import chdir
import warnings
warnings.filterwarnings("ignore")
#chdir("/Users/peter/Workspace/HypDB/server/resources/")
import sys
print(sys.path)
sys.path = ['.'] + sys.path
print(sys.path)

import os
cwd = os.getcwd()
print(cwd)

"""
Bias Resource

Computes bias statistics
"""

import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)

import json
import falcon

# HypDB imports
from os import chdir
from FairDB.core.cov_selection import FairDB
from FairDB.core.explanation import top_k_explanation
import FairDB.core.query as sql
from FairDB.core.matching import *
import time
import FairDB.core.simdetec as simp
from FairDB.utils.util import bining,get_distinct
import FairDB.modules.statistics.cit as test

class BiasResource(object):
  """Resource for computing bias statistics"""

  def on_post(self, req, resp):
    #print(req)
    #print(resp)
    #print('helloworld')
    #with open('posttest123.txt', 'w+') as f:
    #    f.write('hello world')
    #    f.write('end')

    """Endpoint for returning bias statistics about a query"""
    
    # Read Data
    data2 = read_from_csv('./resources/data/binadult.csv')
    #data2=data2[data2['maritalstatus'].isin(['Divorced','Nevermarried','Separated','Widowed'])]
    #data2=data2[data2['maritalstatus'].isin(['Divorced','Nevermarried'])]

    # Question: Does sex have any direct or indirect effect on adult income?
    ## Initializes FairDB 
    treatment=['sex']
    outcome=['income']
    detector = FairDB(data2)
    #FairDB parameters
    whitelist = []
    black = ['']  
    fraction = 0.1
    shfraction = 1.1
    method = 'g2'
    pvalue = 0.001
    num_samples = 1000
    loc_num_samples = 100
    debug = False
    coutious = 'full'
    k=3

    ## Naive group-by query, followd by a conditional independance test 
    ate = sql.naive_groupby(data2, treatment, outcome)
    sql.plot(ate,treatment,outcome,'Average High Income','Naive SQL')
    #pval,I=test.ulti_fast_permutation_tst(data2,treatment, outcome, pvalue=pvalue,
    #                                     debug=True,loc_num_samples=10000,
    #                                     num_samples=1000,view=False)
    print('P value',pval,'  (<0.01 depedance)')
    '''
    # Computing parents of the treatment
    start=time.time()
    cov1, par1 = detector.get_parents(treatment, pvalue=pvalue, method=method
                                       , ratio=1, fraction=fraction, num_samples=num_samples,
                                       blacklist=black, whitelist=whitelist, debug=debug, coutious=coutious,loc_num_samples=loc_num_samples,k=k)

    end=time.time()
    print('elapsed time',end-start)
    print('g test',detector.ngtest)
    print('p test',detector.nptest)

    print(cov1)
    print('parents of the treatment:',par1)

    # Computing parents of the outcome
    start=time.time()
    cov2, par2 = detector.get_parents(outcome, pvalue=pvalue, method=method
                                       , ratio=1, fraction=fraction, num_samples=num_samples,
                                       blacklist=black, whitelist=whitelist, debug=debug, coutious=coutious,loc_num_samples=loc_num_samples,k=k)
    end=time.time()
    print('elapsed time',end-start)
    print('g test',detector.ngtest)
    print('p test',detector.nptest)

    print(cov2)
    print('parents',par2)

    covarite1=remove_dup(par1+par2)
    print(covarite1)
    covarite2=remove_dup(cov1+cov2)
    print(covarite2)
    covarite3=remove_dup(par1+cov2)
    print(covarite3)

    covarite3=['workclass', 'age', 'education', 'occupation', 'hoursperweek', 'capitalgain']

    cov2=['hoursperweek', 'relationship', 'occupation', 'educationnum', 'capitalgain']
    cov=['hoursperweek', 'relationship', 'educationnum', 'capitalgain']

    covarite=['maritalstatus']
    len(data2.index)
    outcome

    # Adjusting for parents of the treatment for computing total effect
    ate, matcheddata, adj_set,pur=sql.adjusted_groupby(data2, treatment, outcome,['maritalstatus'],mediatpor=['hoursperweek', 'relationship', 'occupation', 'educationnum', 'capitalgain'],init=['Male'],threshould=0)
    print(adj_set,pur)
    sql.plot(ate,treatment,outcome,'Average income','Adjusted SQL')
    pval,I=test.ulti_fast_permutation_tst(data2,treatment, outcome, covarite1, pvalue=pvalue,
                                           debug=True,loc_num_samples=1000,
                                           num_samples=1000,view=False)
    print('P value',I, pval)

    ate, matcheddata, adj_set,pur=sql.adjusted_groupby(data2, treatment, outcome,covarite1,covarite,['Male'],threshould=0)
    print(adj_set,pur)
    sql.plot(ate,treatment,outcome,'Average income','Adjusted SQL')
    pval,I=test.ulti_fast_permutation_tst(data2,treatment, outcome, covarite1, pvalue=pvalue,
                                           debug=True,loc_num_samples=1000,
                                           num_samples=1000,view=False)
    print('P value',I, pval)

    ate, matcheddata, adj_set,pur=sql.adjusted_groupby(data2, treatment, outcome,
                                                         threshould=0,
                                                         covariates=[],mediatpor=covarite3,init=['Male'])
    print(adj_set,pur)
    sql.plot(ate,treatment,outcome,'Average income','Adjusted SQL')
    pval,I=test.ulti_fast_permutation_tst(data2,treatment, outcome, covarite3, pvalue=pvalue,
                                           debug=True,loc_num_samples=1000,
                                           num_samples=100,view=False)
    print('P value',I, pval)

    covarite3
    cov=['age', 'education', 'hoursperweek', 'capitalgain']


    ate, matcheddata, adj_set,pur=sql.adjusted_groupby(data2, treatment, outcome,cov,threshould=0)
    print(adj_set,pur)
    sql.plot(ate,treatment,outcome,'Average income','Adjusted SQL')
    pval,I=test.ulti_fast_permutation_tst(data2,treatment, outcome, cov, pvalue=pvalue,
                                           debug=True,loc_num_samples=10000,
                                           num_samples=1000,view=False)
    print('P value',I, pval)

    res=get_respon2(data2,treatment, outcome,covarite3)
    print(res)

    res=get_respon2(data2,treatment, outcome,cov)
    print(res)

    res=get_respon2(data2,treatment, outcome,covarite1)
    print(res)

    X=top_k_explanation(data2, treatment, outcome, ['hoursperweek'],k=3)
    X[:5]

    top_k_explanation(data2, treatment, outcome, ['capitalgain'],k=3)

    top_k_explanation(data2, treatment, outcome, ['relationship'],k=3)

    top_k_explanation(data2, treatment, outcome, ['occupation'])
    '''

    # Temporary filler return
    print('post worked')
    resp.content_type = 'application/json'
    resp.status = falcon.HTTP_200
    resp.body = json.dumps({'bias': 'immense'})
    return resp
# Works
#temp = BiasResource()
#temp.on_post('', '')

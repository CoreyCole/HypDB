from os import chdir
import warnings
warnings.filterwarnings("ignore")
#chdir("/Users/peter/Workspace/HypDB/server/resources/")
import sys
#print(sys.path)
#sys.path = ['.'] + sys.path
#print(sys.path)

import os
#cwd = os.getcwd()
#print(cwd)

import reprlib
import pprint

import pandas as pd

"""
Bias Resource

Computes bias statistics
"""

import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)

import csv
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
    try:

        """Endpoint for returning bias statistics about a query"""
        
        # Process request
        params = json.load(req.bounded_stream)
        filename = params['dto']['filename']

        # Convert json of database into csv
        with open('./uploads/' + filename + '.json', 'rb') as f:
            data = json.load(f)
            print(len(data['data']))
            #data = pd.read_json(data)
            print(reprlib.repr(data['data']))
            try:
                os.mkdir('./tmp/')
            except OSError as e:
                print(e)
            with open('./tmp/' + filename, 'w') as g:
                fieldnames = data['data'][0].keys()
                writer = csv.DictWriter(g, fieldnames=fieldnames)
                writer.writeheader()
                for line in data['data']:
                    if len(line) == len(fieldnames):
                        writer.writerow(line)

        # Create data
        data = read_from_csv('./tmp/' + filename)

        # Processwhere clause
        # TODO: need support for multiple where statements separated by or
        # TODO: support in clause
        if 'where' in params['dto']:
            # change = to ==
            addEquals = params['dto']['where'].split('=', 1)
            data = data.query(addEquals[0] + '==' + addEquals[1])

        # Process group by
        treatment = []
        if 'groupingAttributes' in params['dto']:
            for attr in params['dto']['groupingAttributes']:
                treatment.append(attr)

        # Process select
        outcome = []
        if 'outcomes' in params['dto']:
            for attr in params['dto']['outcomes']:
                outcome.append(attr)

        # Initialize FairDB
        detector = FairDB(data)

        # FairDB parameters
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
        
        # Computing parents of the treatment
        start=time.time()
        cov1, par1 = detector.get_parents(treatment, pvalue=pvalue, method=method, ratio=1, fraction=fraction,
                                            num_samples=num_samples, blacklist=black, whitelist=whitelist,
                                            debug=debug, coutious=coutious, loc_num_samples=loc_num_samples, k=k)
        
        end=time.time()
        print('elapsed time',end-start)
        print('g test',detector.ngtest)
        print('p test',detector.nptest)

        print(cov1)
        print('parents of the treatment:',par1)

        # Computing parents of the outcome
        start=time.time()
        cov2, par2 = detector.get_parents(outcome, pvalue=pvalue, method=method, ratio=1, fraction=fraction,
                                            num_samples=num_samples, blacklist=black, whitelist=whitelist,
                                            debug=debug, coutious=coutious, loc_num_samples=loc_num_samples, k=k)
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

        '''covarite3=['workclass', 'age', 'education', 'occupation', 'hoursperweek', 'capitalgain']

        cov2=['hoursperweek', 'relationship', 'occupation', 'educationnum', 'capitalgain']
        cov=['hoursperweek', 'relationship', 'educationnum', 'capitalgain']

        covarite=['maritalstatus']
        outcome

        # Adjusting for parents of the treatment for computing total effect

        ate, matcheddata, adj_set,pur=sql.adjusted_groupby(data2, treatment, outcome,covarite1,covarite,['Male'],threshould=0)

        ate, matcheddata, adj_set,pur=sql.adjusted_groupby(data2, treatment, outcome,
                                                             threshould=0,
                                                             covariates=[],mediatpor=covarite3,init=['Male'])
        print(adj_set,pur)
        covarite3
        cov=['age', 'education', 'hoursperweek', 'capitalgain']


        ate, matcheddata, adj_set,pur=sql.adjusted_groupby(data2, treatment, outcome,cov,threshould=0)
        print(adj_set,pur)

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

        top_k_explanation(data2, treatment, outcome, ['occupation'])'''

        # Temporary filler return
        print('post worked')
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'bias': 'immense'})
        return resp
    except Exception as e:
        print(e)
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_422
        resp.body = 'Error: Please try again with different parameters'
        print(resp)
        return resp
# Works
#temp = BiasResource()
#temp.on_post('', '')

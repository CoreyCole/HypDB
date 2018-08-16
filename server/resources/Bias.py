import warnings
warnings.filterwarnings("ignore")

import reprlib
import pprint

import pandas as pd

"""
Bias Resource

Computes bias statistics
"""
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
from FairDB.utils.util import bining, get_distinct
# import FairDB.modules.statistics.cit as test


class BiasResource(object):
    """Resource for computing bias statistics"""

    def parseWhere(key, value, data):
        # print(key, value, len(data))
        if key == 'AND':
            key0 = next(iter(value[0]))
            key1 = next(iter(value[1]))
            data1 = BiasResource.parseWhere(key0, value[0][key0], data)
            data2 = BiasResource.parseWhere(key1, value[1][key1], data1)
            return data2
        elif key == 'IN':
            if isinstance(value[0], dict):
                key = next(iter(value[0]))
                if key == 'NOT':
                    if not isinstance(value[1], list):
                        value[1] = [value[1]]
                    data = data[~data[value[0][key][0]].isin(value[1])]
                    return data
                else:
                    raise ValueError('Invalid IN statement')
            else:
                if not isinstance(value[1], list):
                    value[1] = [value[1]]
                data = data[data[value[0]].isin(value[1])]
            return data
        elif key == '=':
            data = data.query(value[0] + '==\'' + str(value[1]) + '\'')
            return data
        elif key == '!=':
            data = data.query(value[0] + '!=\'' + str(value[1]) + '\'')
            return data
        else:
            raise ValueError("Supported where operators include 'AND', 'IN', 'NOT IN', '=', and '!='  ")


    def on_post(self, req, resp):
        # try:

            """Endpoint for returning bias statistics about a query"""

            # Process request
            params = json.load(req.bounded_stream)
            # print(json.dumps(params))
            filename = params['filename']
            # Convert json of database into csv
            with open('./uploads/' + filename + '.json', 'rb') as f:
                data = json.load(f)
                #print(len(data['data']))
                #data = pd.read_json(data)
                #print(reprlib.repr(data['data']))
                with open('./tmp/' + filename, 'w') as g:
                    fieldnames = data['data'][0].keys()
                    writer = csv.DictWriter(g, fieldnames=fieldnames)
                    writer.writeheader()
                    for line in data['data']:
                        if len(line) == len(fieldnames):
                            writer.writerow(line)
            # Create data
            data = read_from_csv('./tmp/' + filename)
            print('data size: ', len(data))

            # Processwhere clause
            # TODO: need support for multiple where statements separated by or
            # TODO: support in clause
            # data = data[data['carrier'].isin(['AA', 'UA'])]
            # data = data[data['origin'].isin(['COS', 'MFE', 'MTJ', 'ROC'])]
            # print(len(data))

            if 'where' in params and params['where'] != 'undefined':
                #print(len(data))
                #data = data.query("carrier in ('UA', 'AA') and origin in ('COS', 'MFE', 'MTJ', 'ROC') and carrier != 'UA'")
                #print(len(data))
                key = next(iter(params['where']))
                data = BiasResource.parseWhere(key, params['where'][key], data)
                print('data size (post where clause): ', len(data))
            if len(data) == 0:
                raise ValueError('No rows remaining in database after where clause')
                #if params['where']:
                #    # change = to ==
                #    addEquals = params['where'].split('=', 1)
                #    data = data.query(addEquals[0] + '==' + addEquals[1])

            # Process group by
            treatment = []
            if 'groupingAttributes' in params:
                if params['groupingAttributes']:
                    for attr in params['groupingAttributes']:
                        treatment.append(attr)

            # Process select
            outcome = [params['outcome']]
            # if 'outcomes' in params:
            #     if params['outcomes']:
            #         for attr in params['outcomes']:
            #             outcome.append(attr)

            # Initialize FairDB
            detector = FairDB(data)

            # FairDB parameters
            whitelist = []
            black = ['']
            fraction = 1
            shfraction = 1
            method = 'g2'
            pvalue = 0.01
            num_samples = 1000
            loc_num_samples = 100
            debug = False
            coutious = 'no'
            k = 3

            # Naive group-by query, followd by a conditional independance test
            grouping_attributes = []
            ate_list = []
            for treat in treatment:
                grouping_attributes.append(treat)
                ate = sql.naive_groupby(data, grouping_attributes[::-1], outcome)
                ate_step = sql.plot(ate, grouping_attributes, outcome)
                ate_list.append(ate_step)
            outJSON = {'ate': ate_list}
            print(outJSON)

            # Computing parents of the treatment
            start = time.time()
            cov1, par1 = detector.get_parents(treatment, pvalue=pvalue, method=method, ratio=1, fraction=fraction,
                                              num_samples=num_samples, blacklist=black, whitelist=whitelist,
                                              debug=debug, coutious=coutious, loc_num_samples=loc_num_samples, k=k)

            # end=time.time()
            # print('elapsed time',end-start)
            # print('g test',detector.ngtest)
            # print('p test',detector.nptest)

            print('covariates of the treatment:', cov1)
            print('parents of the treatment:', par1)

            # Computing parents of the outcome
            # start=time.time()
            cov2, par2 = detector.get_parents(outcome, pvalue=pvalue, method=method, ratio=1, fraction=fraction,
                                              num_samples=num_samples, blacklist=black, whitelist=whitelist,
                                              debug=debug, coutious=coutious, loc_num_samples=loc_num_samples, k=k)

            sql.graph(cov1, par1, cov2, par2, treatment, outcome, outJSON)

            # end=time.time()
            # print('elapsed time',end-start)
            # print('g test',detector.ngtest)
            # print('p test',detector.nptest)

            print('covariates of the outcome', cov2)
            print('parents of the outcome', par2)
            '''
            covarite1=remove_dup(par1+par2)
            print(covarite1)
            covarite2=remove_dup(cov1+cov2)
            print(covarite2)
            covarite3=remove_dup(par1+cov2)
            print(covarite3)'''

            # covarite3=['workclass', 'age', 'education', 'occupation', 'hoursperweek', 'capitalgain']

            # cov2=['hoursperweek', 'relationship', 'occupation', 'educationnum', 'capitalgain']
            # cov=['hoursperweek', 'relationship', 'educationnum', 'capitalgain']

            # covarite=['maritalstatus']
            # outcome

            # Adjusting for parents of the treatment for computing total effect

            #ate, matcheddata, adj_set,pur=sql.adjusted_groupby(data2, treatment, outcome,covarite1,covarite,['Male'],threshould=0)

            # ate, matcheddata, adj_set,pur=sql.adjusted_groupby(data2, treatment, outcome,
            #                                                     threshould=0,
            #                                                     covariates=[],mediatpor=covarite3,init=['Male'])
            # print(adj_set,pur)
            # covarite3
            #cov=['age', 'education', 'hoursperweek', 'capitalgain']

            #ate, matcheddata, adj_set,pur=sql.adjusted_groupby(data2, treatment, outcome,cov,threshould=0)
            # print(adj_set,pur)

            #res=get_respon2(data2,treatment, outcome,covarite3)
            # print(res)

            #res=get_respon2(data2,treatment, outcome,cov)
            # print(res)

            #res=get_respon2(data2,treatment, outcome,covarite1)
            # print(res)

            #X=top_k_explanation(data2, treatment, outcome, ['hoursperweek'],k=3)
            # X[:5]

            #top_k_explanation(data2, treatment, outcome, ['capitalgain'],k=3)

            #top_k_explanation(data2, treatment, outcome, ['relationship'],k=3)

            #top_k_explanation(data2, treatment, outcome, ['occupation'])

            # Temporary filler return
            print('post worked')
            resp.content_type = 'application/json'
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(outJSON)
            return resp
        # except Exception as e:
        #     print(e)
        #     resp.content_type = 'application/json'
        #     resp.status = falcon.HTTP_422
        #     resp.body = str(e)
        #     return resp
# Works
#temp = BiasResource()
#temp.on_post('', '')

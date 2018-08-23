"""
Bias Resource

Computes bias statistics
"""
import warnings
warnings.filterwarnings("ignore")

import csv
import json
import falcon
import pandas as pd
from itertools import chain, combinations

# HypDB imports
from os import chdir
from FairDB.core.cov_selection import FairDB
from FairDB.core.explanation import top_k_explanation
import FairDB.core.query as sql
from FairDB.core.matching import *
import time
import FairDB.core.simdetec as simp
from FairDB.utils.util import bining, get_distinct
from FairDB.modules.infotheo.info_theo import *


class BiasResource(object):
    """Resource for computing bias statistics"""

    def powerset(self, iterable):
        s = list(iterable)
        return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

    def minCMI(self, treatment, outcome, data, cov1, cov2=[]):
        subset = []
        cache = {}
        info = Info(data)
        #print(treatment, outcome, cov1 + cov2)
        for attrs in BiasResource.powerset(set(cov1 + cov2)):
            cmi1 = info.CMI(treatment, outcome, list(attrs))
            cmi2 = info.CMI(treatment, outcome, subset)
            if cmi1 < cmi2:
                subset = list(attrs)
        print(subset)
        return subset

    def parseWhere(key, value, data):
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
            data = data.query(value[0] + '==' + str(value[1]))
            return data
        elif key == '!=':
            data = data.query(value[0] + '!=' + str(value[1]))
            return 
        elif key == '>':
            data = data.query(value[0] + '>' + str(value[1]))
            return data
        elif key == '>=':
            data = data.query(value[0] + '>=' + str(value[1]))
            return data
        elif key == '<':
            data = data.query(value[0] + '<' + str(value[1]))
            return data
        elif key == '<=':
            data = data.query(value[0] + '<=' + str(value[1]))
            return data
        else:
            raise ValueError("Supported where operators include 'AND', 'IN', 'NOT IN', '=', '!=', '>', '>=', '<', and '<='")

    def on_post(self, req, resp):
        #try:

            """Endpoint for returning bias statistics about a query"""

            # Process request
            params = json.load(req.bounded_stream)
            print(json.dumps(params))
            filename = params['filename']

            data = read_from_csv('./tmp/' + filename)
            # print('data size: ', len(data))

            # Process where clause
            # TODO: need support for multiple where statements separated by or
            if 'where' in params and params['where'] != 'undefined':
                print(params['where'])
                key = next(iter(params['where']))
                data = BiasResource.parseWhere(key, params['where'][key], data)
                # print('data size (post where clause): ', len(data))
            if len(data) == 0:
                raise ValueError('No rows remaining in database after where clause')

            # Process group by
            treatment = []
            if 'groupingAttributes' in params:
                if params['groupingAttributes']:
                    for attr in params['groupingAttributes']:
                        treatment.append(attr)

            # Process select
            outcome = [params['outcome']]

            # Initialize FairDB
            detector = FairDB(data)

            # FairDB parameters


            whitelist = []
            black = []
            if filename == 'finpe2.csv':
                whitelist = ['origin']
                black = ['destcityname', 'dest', 'origincityname']
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
            ate = sql.naive_groupby(data, treatment, outcome)
            ate_data = sql.plot(ate, treatment, outcome)
            outJSON = {'naiveAte': ate_data}
            print(outJSON)

            # old code for getting ate for each grouping attribute
            # going to need to do the reverse array trick again once we know the most biased covariate
            # grouping_attributes = []
            # ate_list = []
            # for treat in treatment:
            #     grouping_attributes.append(treat)
            #     ate = sql.naive_groupby(data, grouping_attributes[::-1], outcome)
            #     ate_step = sql.plot(ate, grouping_attributes, outcome)
            #     ate_list.append(ate_step)
            # outJSON = {'ate': ate_list}

            # Computing parents of the treatment
            cov1, par1 = detector.get_parents(treatment, pvalue=pvalue, method=method, ratio=1, fraction=fraction,
                                              num_samples=num_samples, blacklist=black, whitelist=whitelist,
                                              debug=debug, coutious=coutious, loc_num_samples=loc_num_samples, k=k)

            print('treatment: ', treatment)
            print('covariates of the treatment: ', cov1)
            print('parents of the treatment: ', par1)

            # Computing parents of the outcome
            cov2, par2 = detector.get_parents(outcome, pvalue=pvalue, method=method, ratio=1, fraction=fraction,
                                              num_samples=num_samples, blacklist=black, whitelist=whitelist,
                                              debug=debug, coutious=coutious, loc_num_samples=loc_num_samples, k=k)
    
            sql.graph(cov1, par1, cov2, par2, treatment, outcome, outJSON)

            print('outcome: ', outcome)
            print('covariates of the outcome: ', cov2)
            print('parents of the outcome: ', par2)

            # get most responsible attribute
            res = get_respon(data, treatment, outcome, list(set(cov1 + cov2)))
            print(res)

            # treatment.append('origin')
            # print(treatment)
            t2 = treatment.copy()
            #if max(res, key=res.get)
            t2.append(max(res, key=res.get))
            print(t2)
            ate2 = sql.naive_groupby(data, t2[::-1], outcome)
            print(ate2)
            ate_data2 = sql.plot(ate2, t2, outcome)
            outJSON['responsibleAte'] = ate_data2

            '''
            # Adjusting for parents of the treatment for computing total effect
            # mediatpor and init not needed for total effect
            de = None


            # init for direct effect
            # pass list to iloc to guarantee dataframe
            highestGroup = ate.iloc[[ate[outcome[0]].idxmax()]]
            init = highestGroup[treatment].values[0]

            # direct effect
            if par1 and par2:
                de, matcheddata, adj_set,pur=sql.adjusted_groupby(data, treatment, outcome, par1, par2, init)
                print('de1', de)

            print(data)
            cmi1 = BiasResource.minCMI(treatment, outcome, data, cov1, cov2)
            print('cmi1 = ', cmi1)
            if cmi1:
                alt1 = []
                alt2 = []
                for attr in cmi1:
                    if attr in cov2 and attr != outcome:
                        alt2.append(attr)
                    elif attr in cov1 and attr != outcome:
                        alt1.append(attr)
                    else:
                        # This should never happen
                        raise ValueError('attr == outcome')
                if alt1 and alt2:
                    de, matcheddata, adj_set,pur=sql.adjusted_groupby(data, treatment, outcome, alt1, alt2, init)
                    print('de2', de)


            # total effect
            if par1:
                te, matcheddata, adj_set,pur=sql.adjusted_groupby(data, treatment, outcome, par1)
                print('te1', te)

            cmi2 = BiasResource.minCMI(treatment, outcome, data, cov1)
            print('cmi2 = ', cmi2)
            if cmi2:
                alt1 = []
                for attr in cmi2:
                    if attr in cov1 and attr != outcome:
                        alt1.append(attr)
                    else:
                        raise ValueError('attr == outcome')
                if alt1:
                    te, matcheddata, adj_set,pur=sql.adjusted_groupby(data, treatment, outcome, cmi2)
                    print('te2', te)
            '''

            outJSON['cov_treatment'] = cov1
            outJSON['cov_outcome'] = cov2
            outJSON['responsibility'] = res

            outJSON['fine_grained'] = {'treatment': treatment, 'outcome': outcome, 'attributes': {}}
            print(data.columns.values, treatment, outcome, [*res])
            for attr in set([*res]) - set(treatment) - set(outcome):
                X=top_k_explanation(data, treatment, outcome, [attr], k=3)
                print(X.loc[:, attr: outcome[0]])
                #print(X)
                columns = list(X.columns.values[:3])
                columns.append('totalCorrelation')
                rows = []
                for index, row in X.iterrows():
                    row_data = {}
                    for column in columns:
                        if (column == 'totalCorrelation'):
                            column = 'TotalCorrelation'
                        row_data[column] = row[column]
                    row_data['totalCorrelation'] = str(row['TotalCorrelation'])
                    rows.append(row_data)
                #print(rows)
                #print(columns)
                outJSON['fine_grained']['attributes'][attr] = {'columns': columns, 'rows': rows}
            print(json.dumps(outJSON))


            # REMOVE THIS AFTER COREY's BUGFIX
            # params['whereString'] = "Carrier in ('AA','UA') AND Airport in ('COS','MFE','MTJ','ROC')"

            # BLOCKS
            outJSON['rewritten-sql'] = []
            outJSON['rewritten-sql'].append('WITH Blocks AS')
            outJSON['rewritten-sql'].append('  (')
            select = '    SELECT '
            select += treatment[0]
            for attribute in list(set(cov1 + cov2)):
                select += ', ' + attribute
            select += ', avg(' + outcome[0] + ') AS avge' 
            outJSON['rewritten-sql'].append(select)
            outJSON['rewritten-sql'].append('    FROM ' + params['filename'][:-4])
            if params['whereString'] and params['whereString'] != 'undefined':
                outJSON['rewritten-sql'].append('    WHERE ' + params['whereString'])
            group = '    GROUP BY '
            group += treatment[0]
            for attribute in list(set(cov1 + cov2)):
                group += ', ' + attribute
            outJSON['rewritten-sql'].append(group)
            outJSON['rewritten-sql'].append('  ),')

            # WEIGHTS
            outJSON['rewritten-sql'].append('Weights AS')
            outJSON['rewritten-sql'].append('  (')
            select = '    SELECT '
            for attribute in list(set(cov1 + cov2)):
                select += attribute + ', '
            select += 'count(*) / '
            outJSON['rewritten-sql'].append(select)

            outJSON['rewritten-sql'].append('      (')
            outJSON['rewritten-sql'].append('        SELECT count(*)')
            outJSON['rewritten-sql'].append('        FROM ' + params['filename'][:-4])
            if params['whereString'] and params['whereString'] != 'undefined':
                outJSON['rewritten-sql'].append('        WHERE ' + params['whereString'])
            outJSON['rewritten-sql'].append('      ) AS W')
            outJSON['rewritten-sql'].append('    FROM ' + params['filename'][:-4])
            if params['whereString'] and params['whereString'] != 'undefined':
                outJSON['rewritten-sql'].append('    WHERE ' + params['whereString'])
            group = '    GROUP BY '
            for attribute in list(set(cov1 + cov2)):
                group += attribute + ', '
            if group[-2:] == ', ':
                group = group[:-2]
            outJSON['rewritten-sql'].append(group)
            outJSON['rewritten-sql'].append('    HAVING count(DISTINCT ' + treatment[0] + ') = 2')
            outJSON['rewritten-sql'].append('  )')

            outJSON['rewritten-sql'].append('SELECT ' + treatment[0] + ', sum(avge * W)')
            outJSON['rewritten-sql'].append('FROM Blocks, Weights')
            outJSON['rewritten-sql'].append('GROUP BY ' + treatment[0])
            where = 'WHERE Blocks.'
            for attribute in list(set(cov1 + cov2)):
                where += attribute + ' = Weights.' + attribute + ' AND '
                outJSON['rewritten-sql'].append(where)
                where = '  Blocks.'

            if outJSON['rewritten-sql'][-1][-5:] == ' AND ':
                outJSON['rewritten-sql'][-1] = outJSON['rewritten-sql'][-1][:-5]

            for line in outJSON['rewritten-sql']:
                print(line)

            # Temporary filler return
            print('post worked')

            resp.content_type = 'application/json'
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(outJSON)
            return resp
        #except Exception as e:
        #   print(e)
        #   resp.content_type = 'application/json'
        #   resp.status = falcon.HTTP_422
        #   resp.body = str(e)
        #   return resp

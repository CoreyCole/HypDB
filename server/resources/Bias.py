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
import FairDB.modules.statistics.cit as test


class BiasResource(object):
    """Resource for computing bias statistics"""

    # def powerset(iterable):
    #     s = list(iterable)
    #     return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

    # def minCMI(treatment, outcome, data, cov1, cov2=[]):
    #     #print(info.cmi())
    #     subset = []
    #     cache = {}
    #     info = Info(data)
    #     #print(info.CMI(treatment, outcome, ['distancegroup', 'origin']))
    #     #print(info.CMI(treatment, outcome, ['crsdeptime', 'year']))
    #     #print(info.CMI(treatment, outcome, ['year', 'arrdelay', 'origin', 'distancegroup']))
    #     #print(treatment, outcome, cov1 + cov2)
    #     for attrs in BiasResource.powerset(set(cov1 + cov2)):
    #         #print(list(attrs))
    #         cmi1 = info.CMI(treatment, outcome, list(attrs))
    #         cmi2 = info.CMI(treatment, outcome, subset)
    #         if cmi1 < cmi2:
    #             subset = list(attrs)
    #     return subset

    def writeQuery(treatment, outcome, filename, whereString, naive=True, covariates=[]):
        query = []
        if naive:
            query.append('SELECT ' + outcome[0])
            query.append('FROM ' + filename)
            if whereString and whereString != 'undefined':
                query.append('WHERE ' + whereString)
            if len(treatment) > 1:
                query.append('GROUP BY ' + treatment[0] + ', ' + treatment[1])
            else:
                query.append('GROUP BY ' + treatment[0])
        else:
            # BLOCKS
            query.append('WITH Blocks AS')
            query.append('  (')
            select = '    SELECT '
            select += treatment[0] + ', '
            for attribute in covariates:
                select += attribute + ', '
                if len(select) > 40:
                    query.append(select)
                    select = '      '
            select += 'avg(' + outcome[0] + ') AS avge' 
            query.append(select)
            query.append('    FROM ' + filename)
            if whereString and whereString != 'undefined':
                where = '    WHERE '
                for word in whereString.split(' '):
                    where += word + ' '
                    if len(where) > 40:
                        query.append(where)
                        where = '      '
                if where != '      ':
                    query.append(where)
            group = '    GROUP BY '
            group += treatment[0] + ', '
            for attribute in covariates:
                group += attribute + ', '
                if len(group) > 40:
                    query.append(group)
                    group = '      '
            if group[-2:] == ', ':
                group = group[:-2]
            if group != '      ':
                query.append(group)
            query.append('  ),')

            # WEIGHTS
            query.append('Weights AS')
            query.append('  (')
            select = '    SELECT '
            for attribute in covariates:
                select += attribute + ', '
                if len(select) > 40:
                    query.append(select)
                    select = '      '
            select += 'count(*) / '
            query.append(select)
            query.append('      (')
            query.append('        SELECT count(*)')
            query.append('        FROM ' + filename)
            if whereString and whereString != 'undefined':
                where = '        WHERE '
                for word in whereString.split(' '):
                    where += word + ' '
                    if len(where) > 40:
                        query.append(where)
                        where = '          '
                if where != '          ':
                    query.append(where)
            query.append('      ) AS W')
            query.append('    FROM ' + filename)
            if whereString and whereString != 'undefined':
                where = '    WHERE '
                for word in whereString.split(' '):
                    where += word + ' '
                    if len(where) > 40:
                        query.append(where)
                        where = '      '
                if where != '      ':
                    query.append(where)
            group = '    GROUP BY '
            for attribute in covariates:
                group += attribute + ', '
                if len(group) > 40:
                    query.append(group)
                    group = '      '
            if group[-2:] == ', ':
                group = group[:-2]
            if group != '      ':
                query.append(group)
            query.append('    HAVING count(DISTINCT ' + treatment[0] + ') = 2')
            query.append('  )')

            query.append('SELECT ' + treatment[0] + ', sum(avge * W)')
            query.append('FROM Blocks, Weights')
            query.append('GROUP BY ' + treatment[0])
            where = 'WHERE Blocks.'
            for attribute in covariates:
                where += attribute + ' = Weights.' + attribute + ' AND '
                query.append(where)
                where = '  Blocks.'
            if query[-1][-5:] == ' AND ':
                query[-1] = query[-1][:-5]
        return query 
            

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
                #print(params['where'])
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
            # if filename == 'finpe2.csv':
            #     whitelist = ['origin']
            #     black = ['destcityname', 'dest', 'origincityname']
            fraction = 1
            shfraction = 1
            method = 'g2'
            pvalue = 0.01
            num_samples = 1000
            loc_num_samples = 1000
            if filename == 'AdultData.csv':
                num_samples = 100
                loc_num_samples = 100
            debug = False
            coutious = 'no'
            k = 3

            # Naive group-by query, followd by a conditional independance test
            ate = sql.naive_groupby(data, treatment, outcome)
            ate_data = sql.plot(ate, treatment, outcome)
            print(ate)

            low, high, I = test.ulti_fast_permutation_tst(data, treatment, outcome, pvalue=pvalue,
                                                  debug=debug,loc_num_samples=loc_num_samples,
                                                  num_samples=num_samples,view=False)

            low = '%.3f' % (low) if low else 0
            high = '%.3f' % (high) if high else 0
            I = '%.6f' % (I) if I else 0
            print('pval', low, high, I)

            outJSON = {'data' : []}
            outJSON['naiveAte'] = ate_data

            temp_ate = {'type' : 'naiveAte'}
            temp_ate['query'] = BiasResource.writeQuery(treatment, outcome, params['filename'][:-4], params['whereString'])
            temp_ate['chart'] = ate_data
            temp_ate['low'] = low
            temp_ate['high'] = high
            temp_ate['cmi'] = I
            outJSON['data'].append(temp_ate)

            for line in temp_ate['query']:
                print(line)

            #outJSON = {'naiveAte': ate_data}

            print(outJSON)

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

            # cov
            #cov = BiasResource.minCMI(treatment, outcome, data, cov1)
            cov = None
            if par1:
                cov = par1
            else:
                cov = detector.recommend_covarite(treatment, outcome, cov1)
            #cov = ['distancegroup', 'origin']
            for item in cov:
                if item in cov2:
                    cov2.remove(item)
            # med
            #med = BiasResource.minCMI(treatment, outcome, data, cov2)
            med = None
            if par2:
                med = par2
            else:
                med = detector.recommend_covarite(treatment, outcome, cov2)
            #med = ['crsdeptime', 'year']
            
            if treatment[0] in cov:
                cov.remove(treatment[0])
            if treatment[0] in med:
                med.remove(treatment[0])
            if outcome[0] in cov:
                cov.remove(outcome[0])
            if outcome[0] in med:
                med.remove(outcome[0])
            print('cov = ', cov)
            print('med = ', med)
            # get most responsible attribute
            print(treatment, outcome)
            res = get_respon(data, outcome, treatment, list(set(cov + med)))
            for key in res:
                res[key] = "%.3f" % (res[key])
            print('res', res)

            t2 = treatment.copy()
            newRes = {k:v for (k,v) in res.items() if k != outcome[0] and k != treatment[0]}
            if newRes:
                t2.append(max(newRes, key=newRes.get))
                ate2 = sql.naive_groupby(data, t2[::-1], outcome)
                ate_data2 = sql.plot(ate2, t2, outcome)
                print(ate2)
                low, high, I = test.ulti_fast_permutation_tst(data, treatment, outcome, [t2[1]], pvalue=pvalue,
                                                        debug=debug,loc_num_samples=loc_num_samples,
                                                        num_samples=num_samples,view=False)

                low = '%.3f' % (low) if low else 0
                high = '%.3f' % (high) if high else 0
                I = '%.6f' % (I) if I else 0
                print('pval', low, high, I)

                temp_ate = {'type' : 'responsibleAte'}
                temp_ate['query'] = BiasResource.writeQuery(t2, outcome, params['filename'][:-4], params['whereString'])
                temp_ate['chart'] = ate_data2
                temp_ate['low'] = low
                temp_ate['high'] = high
                temp_ate['cmi'] = I
                outJSON['data'].append(temp_ate)
                
                for line in temp_ate['query']:
                    print(line)

            
            # Adjusting for parents of the treatment for computing total effect
            # mediatpor and init not needed for total effect
            de = None

            # init for direct effect
            # pass list to iloc to guarantee dataframe
            highestGroup = ate.iloc[[ate[outcome[0]].idxmax()]]
            init = highestGroup[treatment].values[0]
            print('init = ', init)

            # direct effect
            # if par1 and par2:
            #     de, matcheddata, adj_set,pur=sql.adjusted_groupby(data, treatment, outcome, par1, par2, init)
            #     print('de1', de)
            #     temp_ate = {'type' : 'direct-effect'}
            #     temp_ate['query'] = ''
            #     temp_ate['chart'] = sql.plot(de, treatment, outcome)
            #     outJSON['data'].append(temp_ate)

            
            # print(data)

            # total effect
            # if par1:
            #     te, matcheddata, adj_set,pur=sql.adjusted_groupby(data, treatment, outcome, par1)
            #     print('te1', te)
            #     temp_ate = {'type' : 'rewritten-sql'}
            #     temp_ate['query'] = BiasResource.writeQuery(treatment, outcome, params['filename'][:-4], params['whereString'], naive=False, covariates=par1)
            #     temp_ate['chart'] = sql.plot(te, treatment, outcome)
            #     outJSON['data'].append(temp_ate)
            #     for line in temp_ate['query']:
            #         print(line)

            # DE
            if cov and med:
                de, matcheddata, adj_set,pur=sql.adjusted_groupby(data, treatment, outcome, cov, med, init)
                print('de', de)

                low, high, I = test.ulti_fast_permutation_tst(matcheddata, treatment, outcome, list(set(cov + med)), pvalue=pvalue,
                                                  debug=debug, loc_num_samples=loc_num_samples,
                                                  num_samples=num_samples, view=False)

                low = '%.3f' % (low) if low else 0
                high = '%.3f' % (high) if high else 0
                I = '%.6f' % (I) if I else 0
                print('pval', low, high, I)

                temp_ate = {'type' : 'direct-effect'}
                temp_ate['query'] = ''
                temp_ate['chart'] = sql.plot(de, treatment, outcome)
                temp_ate['low'] = low
                temp_ate['high'] = high
                temp_ate['cmi'] = I
                outJSON['data'].append(temp_ate)
            else:
                outJSON['data'].append({})


            # TE
            if cov:
                te, matcheddata, adj_set,pur=sql.adjusted_groupby(data, treatment, outcome, cov)
                print('te', te)

                low, high, I = test.ulti_fast_permutation_tst(matcheddata, treatment, outcome, cov, pvalue=pvalue,
                                                      debug=debug, loc_num_samples=loc_num_samples,
                                                      num_samples=num_samples, view=False)

                low = '%.3f' % (low) if low else 0
                high = '%.3f' % (high) if high else 0
                I = '%.6f' % (I) if I else 0
                print('pval', low, high, I)

                temp_ate = {'type' : 'total-effect'}
                temp_ate['query'] = BiasResource.writeQuery(treatment, outcome, params['filename'][:-4], params['whereString'], naive=False, covariates=med)
                temp_ate['chart'] = sql.plot(te, treatment, outcome)
                temp_ate['low'] = low
                temp_ate['high'] = high
                temp_ate['cmi'] = I
                outJSON['data'].append(temp_ate)
            else:
                outJSON['data'].append({})

            for line in temp_ate['query']:
                print(line)

            outJSON['covariates'] = cov
            outJSON['mediator'] = med
            # outJSON['cov_treatment'] = cov1
            # outJSON['cov_outcome'] = cov2
            outJSON['responsibility'] = res

            outJSON['fine_grained'] = {'treatment': treatment, 'outcome': outcome, 'attributes': {}}
            # print(data.columns.values, treatment, outcome, [*res])
            for attr in set([*res]) - set(treatment) - set(outcome):
                X=top_k_explanation(data, treatment, outcome, [attr], k=10)
                print(X.loc[:, attr: outcome[0]])
                #print(X)
                columns = list(X.columns.values[:3])
                #columns.append('totalCorrelation')
                rows = []
                for index, row in X.iterrows():
                    row_data = {}
                    for column in columns:

                        #if (column == 'totalCorrelation'):
                        #    column = 'TotalCorrelation'
                        row_data[column] = row[column]
                    #row_data['totalCorrelation'] = str(row['TotalCorrelation'])
                    rows.append(row_data)
                #print(rows)
                #print(columns)
                outJSON['fine_grained']['attributes'][attr] = {'columns': columns, 'rows': rows}
            print(json.dumps(outJSON))

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

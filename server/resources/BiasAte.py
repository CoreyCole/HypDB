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


class BiasAteResource(object):
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
        """endpoint for returning naive group by query results"""
        # Process request
        params = json.load(req.bounded_stream)
        # print(json.dumps(params))
        filename = params['filename']
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

        # Naive group-by query, followd by a conditional independance test
        ate = sql.naive_groupby(data, treatment, outcome)
        ate_data = sql.plot(ate, treatment, outcome)
        outJSON = {
            'naiveAte': ate_data,
            'graph': {
                'correlation': {
                    'outcome': [outcome],
                    'treatment': [treatment]
                }
            }
        }

        print('post worked')
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(outJSON)
        return resp
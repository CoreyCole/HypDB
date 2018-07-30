
from math import *
import numpy as np
from FairDB.utils.read_data import *
from FairDB.utils.util import *
import numpy as np
from itertools import combinations, permutations

def _build_graph(ranks):
    n_voters, n_candidates = ranks.shape
    edge_weights = np.zeros((n_candidates, n_candidates))
    for i, j in combinations(range(n_candidates), 2):
        preference = ranks[:, i] - ranks[:, j]
        h_ij = np.sum(preference < 0)  # prefers i to j
        h_ji = np.sum(preference > 0)  # prefers j to i
        if h_ij > h_ji:
            edge_weights[i, j] = h_ij - h_ji
        elif h_ij < h_ji:
            edge_weights[j, i] = h_ji - h_ij
    return edge_weights


def rankaggr_lp(ranks):
    """Kemeny-Young optimal rank aggregation"""

    n_voters, n_candidates = ranks.shape

    # maximize c.T * x
    edge_weights = _build_graph(ranks)
    c = -1 * edge_weights.ravel()

    idx = lambda i, j: n_candidates * i + j

    # constraints for every pair
    pairwise_constraints = np.zeros(((n_candidates * (n_candidates - 1)) / 2,
                                     n_candidates ** 2))
    for row, (i, j) in zip(pairwise_constraints,
                           combinations(range(n_candidates), 2)):
        row[[idx(i, j), idx(j, i)]] = 1

    # and for every cycle of length 3
    triangle_constraints = np.zeros(((n_candidates * (n_candidates - 1) *
                                      (n_candidates - 2)),
                                     n_candidates ** 2))
    for row, (i, j, k) in zip(triangle_constraints,
                              permutations(range(n_candidates), 3)):
        row[[idx(i, j), idx(j, k), idx(k, i)]] = 1

    constraints = np.vstack([pairwise_constraints, triangle_constraints])
    constraint_rhs = np.hstack([np.ones(len(pairwise_constraints)),
                                np.ones(len(triangle_constraints))])
    constraint_signs = np.hstack([np.zeros(len(pairwise_constraints)),  # ==
                                  np.ones(len(triangle_constraints))])  # >=

    obj, x, duals = lp_solve(c, constraints, constraint_rhs, constraint_signs,
                             xint=range(1, 1 + n_candidates ** 2))

    x = np.array(x).reshape((n_candidates, n_candidates))
    aggr_rank = x.sum(axis=1)

    return obj, aggr_rank

def kendalltau_dist(rank_a, rank_b):
    tau = 0
    n_candidates = len(rank_a)
    for i, j in combinations(range(n_candidates), 2):
        tau += (np.sign(rank_a[i] - rank_a[j]) ==
                -np.sign(rank_b[i] - rank_b[j]))
    return tau

def rankaggr_brute(ranks):
    min_dist = np.inf
    best_rank = None
    n_voters, n_candidates = ranks.shape
    for candidate_rank in permutations(range(n_candidates)):
        dist = np.sum(kendalltau_dist(candidate_rank, rank) for rank in ranks)
        if dist < min_dist:
            min_dist = dist
            best_rank = candidate_rank
    return min_dist, best_rank

def top_k_explanation(data, treatment, outcome, covariate, k=5, method='2', debug=False):
    # The function returnm top k core for a group by SQL query
    #
    #
    n = len(data.index)
    cov_states = data[covariate].drop_duplicates().values
    tre_states = data[treatment].drop_duplicates().values
    out_states = data[outcome].drop_duplicates().values
    messure_dic = dict()
    explanation_df=pd.DataFrame(columns =  [covariate[0],treatment[0], outcome[0],'SumofRanks',covariate[0]+'->'+treatment[0],covariate[0]+'->'+outcome[0],'RankofTotalCorrelation','TotalCorrelation'])
    if method:
        for out in out_states:
            y = data.loc[data[outcome[0]].isin(out)].index.values
            for tre in tre_states:
                x = data.loc[data[treatment[0]].isin(tre)].index.values
                xy = np.intersect1d(x, y)
                px = len(x) / n
                py = len(y) / n
                pxy = len(xy) / n
                if px == 0 or py == 0 or pxy == 0:
                    continue
                Ixy = (pxy * log(pxy / (px * py)))
                for cv in cov_states:
                    z = data.loc[data[covariate[0]].isin(cv)].index.values
                    xz = np.intersect1d(x, z)
                    yz = np.intersect1d(y, z)
                    xyz = np.intersect1d(xy, z)
                    pz = len(z) / n
                    pxz = len(xz) / n
                    pyz = len(yz) / n
                    pxyz = len(xyz) / n
                    if pz == 0 or py == 0 or px == 0 or pxyz == 0:
                        continue
                    Iyz = pyz * log(pyz / (py * pz))
                    Ixz = pxz * log(pxz / (px * pz))
                    #                    if method=='tc':
                    tc = pxyz * log(pxyz / (px * py * pz))
                    rank1 = Ixz  # /(px*log(px))
                    rank2 = Iyz  # /(py*log(py))
                    #key = str(treatment[0]) + ': ' + str(tre[0])+ ' <--  ' + \
                    #      str(covariate[0]) + ': ' + str(cv[0])+ '  -->  ' + str(outcome[0]) + ': ' + str(out[0])
                    key = str(cv[0])+','+str(tre[0])+ ','+str(out[0])
                    if tc>0:
                        messure_dic[key] = [rank1, rank2, tc]
        # res1 = sorted(messure_dic.items(), key=lambda e: e[1][0])
        # print(messure_dic)
        ranked_res1 = dict_to_rank(messure_dic, 0)
        ranked_res2 = dict_to_rank(messure_dic, 1)
        ranked_res3 = dict_to_rank(messure_dic, 2)
        scorelist=[ranked_res1,ranked_res2]
        #FLRA = FullListRankAggregator()
        #aggRanks = FLRA.aggregate_ranks(scorelist)
        col=list(ranked_res1.keys())
        rank1=[]
        rank2=[]
        rank3=[]
        for item in col:
            rank1.insert(0, ranked_res1[item])
            rank2.insert(0, ranked_res2[item])
            rank3.insert(0, ranked_res3[item])
        rank1.reverse()
        rank2.reverse()
        rank3.reverse()
        ranked_res1_val=ranked_res1.values()
        rank1=np.array(rank1)
        rank2 = np.array(rank2)
        rank3 = np.array(rank3)
        lent=7
        if method == '3':
            print('3 ranks aggregated')
            ranks = np.array([rank1[0:lent],
                             rank2[0:lent],
                             rank3[0:lent]])
        else:
            print('2 ranks aggregated')
            ranks = np.array([rank1[0:lent],
                                  rank2[0:lent]])
        #dist, aggr = rankaggr_brute(ranks)
        #_, aggr = rankaggr_lp(ranks)
        cols=messure_dic.keys()
        #[cols[i] for i in np.argsort(aggr)]
        #np.argsort(aggr)
        col=col[0:lent]
        aggRanks = dict()
        i=0
        for item in col:
            #aggRanks[item]=aggr[i]
            i=i+1
        explanation = dict()
        for item in col:
                if messure_dic[item][2]<0:
                    continue
                #print(ranked_res1[item])
                #print(ranked_res2[item])
                agg=(ranked_res1[item]+ranked_res2[item]+ranked_res3[item])*(abs(ranked_res1[item]-ranked_res2[item])+1)
                #print(agg)
                explanation[item] = [agg,ranked_res1[item] , ranked_res2[item], ranked_res3[item], messure_dic[item][2]]

        #res = dict()

        res = sorted(explanation.items(), key=lambda e: e[1][0])
        res = res[:k]
        for exp in res:
            item=exp[0].split(',')+exp[1]
            #print(item)
            explanation_df.loc[k] =item  # adding a row
            explanation_df.index = explanation_df.index - 1  # shifting index
        #df = explanation_df.sort()
        return explanation_df


if __name__ == '__main__':

    data=read_from_csv('/Users/babakmac/Documents/XDBData/binadult.csv')
    treatment = ['sex']
    outcome = ['income']
    cov=['maritalstatus']
    top=top_k_explanation(data,treatment,outcome,cov)
    print(top)
    '''
    data = read_from_csv('/Users/babakmac/Documents/XDBData/staples(b).csv')
    treatment = ['income']
    outcome = ['price']
    cov=['distance']
    top=top_k_explanation(data,treatment,outcome,cov)
    print(top)
'''
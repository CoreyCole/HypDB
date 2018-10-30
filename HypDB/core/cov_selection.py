import copy
import hypdb.modules.statistics.cit as test
from hypdb.utils.read_data import *
import hypdb.modules.infotheo.info_theo as info
from hypdb.utils.util import *
import time
from scipy.stats import chi2,spearmanr,pearsonr
from math import sqrt
from pprint import pprint
import itertools
def findsubsets(S,m):
    return set(itertools.combinations(S, m))
def diff(list1, list2):
        if len(list1)==0:
          return list2
        if len(list2)==0:
          return list1
        return [x for x in list1 if x not in list2]

class hypdb(object):
    def recommend_covarite(self, treatment, outcome, potential):
        inf = info.Info(self.data)
        init_cmi = inf.CMI(treatment,outcome)
        recom_cov=[]
        while 1>0:
            cur_recom_cov=recom_cov.copy()
            for item in potential:
                    ad_cmi=inf.CMI(treatment, outcome, [item] + recom_cov)
                    if  ad_cmi<init_cmi:
                        if item not in recom_cov:
                            recom_cov=[item] + recom_cov
                            init_cmi=ad_cmi
            if  cur_recom_cov ==recom_cov:
                break
        return recom_cov

    def __init__(self, data, fraction=1,cube=False, database=False,cubename='',tablename=''):
        self.orgdata = data
        self.data = data
        #self.treatmentlevel = get_distinct(self.data,treatment)
        #self.size = len(self.data.index)
        self.features = self.data.columns.values
        self.causes = dict()
        self.datainfo=info.Info(data,cube=cube, database=database,cubename=cubename,tablename=tablename)
        #if fraction!=1:
        #    self.sample = self.data.sample(frac=fraction, replace=False)
        #self.saminfo = info.Info(self.sample)
        #else:
        self.saminfo=self.datainfo
        self.sample=data
        self.pre_com_view=[]
        self.isshrink=False

        self.size=len(self.data.index)
        self.rev_mbs=dict()
        self.mbs=dict()
        self.nptest=0
        self.ngtest=0
        self.flag=True
        self.parents=dict()
        self.childers=dict()
        self.cithash=dict()




    def reset(self):
        self.rev_mbs.clear()
        self.mbs.clear()
        self.nptest=0
        self.ngtest=0
        self.flag=True
        self.parents.clear()
        self.childers.clear()
        self.cithash.clear()
    def CIT(self,X, Y, Z=[], method='g2', pvalue=0.05, debug=False, fraction=1, coutious=False, ratio=0.1,
            num_samples=1000, loc_num_samples=100,maxmcs=100):

        self.flag = True
        start=time.time()
        if method not in ['g2','fpermu','hybrid']:
            raise ValueError('Invalid method')
        if debug:
            print(str(X) + ',' + str(Y) + '|' + str(Z))
        if method == 'fpermu':
            if self.isshrink:
              pval, I = test.ulti_fast_permutation_tst(self.pre_com_view, X, Y, Z, pvalue=pvalue, ratio=ratio, debug=debug,
                                                     num_samples=num_samples,
                                                     loc_num_samples=loc_num_samples, fraction=fraction,view=True,maxmc=maxmcs)
            else:
                pval, I = test.ulti_fast_permutation_tst(self.data, X, Y, Z, pvalue=pvalue, ratio=ratio,
                                                         debug=debug,
                                                         num_samples=num_samples,
                                                         loc_num_samples=loc_num_samples, fraction=fraction, view=False,maxmc=maxmcs)
            self.nptest+=1
            if debug:
                print('I: ' + str(I))
                print("p-value: " + str(pval))
            if pval > pvalue:
                res = 1
            else:
                res = 0
            #self.cithash[tuple(X + Y + Z)] = [res, I]
            return [res, I]
        elif method == 'hybrid':
            self.flag = False
            self.ngtest += 1
            if isinstance(X, str):
                X = tuple([X])
            elif isinstance(X, list):
                X = tuple(X)
            if isinstance(Y, str):
                Y = tuple([Y])
            elif isinstance(Y, list):
                Y = tuple(Y)
            if isinstance(Z, str):
                Z = tuple([Z])
            elif isinstance(Z, list):
                Z = tuple(Z)

            if self.isshrink:
                if self.isshrink:
                    print('good')
                    self.datainfo.data = self.pre_com_view
                    self.datainfo.iscont = True
                    i = self.datainfo.get_distinct(X)
                    j = self.datainfo.get_distinct(Y)
                    if Z:
                        k = self.datainfo.get_distinct(Z)
                    else:
                        k = 1
            else:
                print('bad')
                self.datainfo.iscont = False
                self.datainfo.data = self.data
                i = self.datainfo.get_distinct(X)
                j = self.datainfo.get_distinct(Y)
                if Z:
                    k = self.datainfo.get_distinct(Z)
                else:
                    k = 1
            dof = (i - 1) * (j - 1) * k
            if dof<=self.size/5:
                #self.datainfo.data = self.data
                #self.datainfo.iscont = False
                if self.isshrink:
                    self.datainfo.data = self.pre_com_view
                    self.datainfo.iscont = True
                    I = self.datainfo.CMI(X, Y, Z)

                else:
                    self.datainfo.data = self.data
                    self.datainfo.iscont = False
                    I = self.datainfo.CMI(X, Y, Z)
                gscore = 2 * self.size * I  # /(log(2)/log(10)))
                #dof=(i*j*k-1)-(i+j+k-3)
                pval1 = 1 - chi2.cdf(gscore, dof)
                # pval2=stats.norm.cdf(gscore, (Js-1)*Ks, (Js-1)*Ks)
                res = 0
                self.flag=False
                if debug:
                    print('I: ' + str(I))
                    print('gscore: ' + str(gscore))
                    print('Degree of Fredom: ' + str(dof))
                    print("p-value: " + str(pval1))
                if pval1 < pvalue:
                    res = 0
                else:
                    res = 1
                self.ngtest += 1
            else:
                self.nptest += 1
                if self.isshrink:
                    pval, I = test.ulti_fast_permutation_tst(self.pre_com_view, X, Y, Z, pvalue=pvalue, ratio=ratio,
                                                             debug=debug,
                                                             num_samples=num_samples, loc_num_samples=loc_num_samples,
                                                             fraction=fraction)
                else:
                    pval, I = test.ulti_fast_permutation_tst(self.data, X, Y, Z, pvalue=pvalue, ratio=ratio,
                                                             debug=debug,
                                                             num_samples=num_samples, loc_num_samples=loc_num_samples,
                                                             fraction=fraction,view=False)

                if debug:
                    print('I: ' + str(I))
                    print("p-value: " + str(pval))
                if pval > pvalue:
                    res = 1
                else:
                    res = 0
            return [res, I]

        elif method == 'g2':
            self.flag=False
            self.ngtest += 1
            if isinstance(X, str):
                X = tuple([X])
            elif isinstance(X, list):
                X = tuple(X)
            if isinstance(Y, str):
                Y = tuple([Y])
            elif isinstance(Y, list):
                Y = tuple(Y)
            if isinstance(Z, str):
                Z = tuple([Z])
            elif isinstance(Z, list):
                Z = tuple(Z)
            if self.isshrink:
                if self.isshrink:
                    #print('good')
                    self.datainfo.data = self.pre_com_view
                    self.datainfo.iscont = True
                    #print(len(self.pre_com_view))
                    I = self.datainfo.CMI(X, Y, Z)
                    i = self.datainfo.get_distinct(X)
                    j = self.datainfo.get_distinct(Y)
                    if Z:
                        k = self.datainfo.get_distinct(Z)
                    else:
                        k = 1
            else:
                #print('bad')
                self.datainfo.iscont = False
                #print(len(data.index))
                self.datainfo.data=self.data
                I =  self.datainfo.CMI(X, Y, Z)
                i =  self.datainfo.get_distinct(X)
                j =  self.datainfo.get_distinct(Y)
                n = self.size
                if Z:
                    k =  self.datainfo.get_distinct(Z)
                else:
                    k = 1
            gscore = 2 * self.size * I  # /(log(2)/log(10)))
            dof = (i - 1) * (j - 1) * k
            #dof=(i*j*k-1)-(i+j+k-3)
            pval1 = 1 - chi2.cdf(gscore, dof)
            # pval2=stats.norm.cdf(gscore, (Js-1)*Ks, (Js-1)*Ks)
            res = 0
            if debug:
                print('I: ' + str(I))
                print('gscore: ' + str(gscore))
                print('Degree of Fredom: ' + str(dof))
                print("p-value: " + str(pval1))
            if pval1 < pvalue:
                res = 0
            else:
                res = 1
            end = time.time()
            #print(end-start,Z)
            return [res, I]

    def parent_test(self, x, y, z, alpha=0.0001, pvalue=0.05, method='norm', debug=False):
        res, I = test.CIT(self.data, x, y, z, alpha=alpha, pvalue=pvalue, method=method, coutious=True)
        if debug:
            print('########')
            print(x)
            print(y)
            print(z)
            print('########')
        if res == 0:
            return 1, I  # c and b are parents of x
        else:
            return 0, I  # on or both of them are non-parents of x

    def grow_shrink(self, target, method, maxmc=100,pvalue=0.05,
                    blacklist=None, whitelist=None,  fraction=1,
                    debug=False, coutious=True, ratio=1, loc_num_samples=100, num_samples=1000, istreatment=[], optimized=False):
        self.data = self.orgdata.copy()
        self.datainfo.data=self.orgdata
        self.saminfo.data=self.orgdata
        alpha=20
        flag= 0
        self.isshrink = False
        if isinstance(target,str):
            target=[target]
        startalg = time.time()
        if target[0] in self.mbs.keys():
            boundary = self.mbs[target[0]]
            # print("already computed: ", target, ':::::: white list:', whitelist, 'optimized: ', optimized)
            return boundary, self.causes,0

        if target[0] in self.rev_mbs.keys():
            whitelist = self.rev_mbs[target[0]]
        # print(white)
        boundary=[]

        # print("Computing boundary of: ",target, ':::::: white list:', whitelist, 'optimized: ',optimized)
        optimized=optimized   # if True materlizes selected views
        cndl = copy.copy(self.features)
        cndl = cndl.tolist()
        # remove the blacke lists from the feature list

        if blacklist:
            for item in blacklist:
                if item in cndl:
                    cndl.remove(item)
        # remove the white lists from the feature list
        #if target in self.rev_mbs.keys():
        #    whitelist=remove_dup(whitelist+ detector.rev_mbs[target[0]])

        if whitelist:
            for t in whitelist:
                if cndl.__contains__(t):
                    cndl.remove(t)
        # remove the target variables from the feature list
        if target[0] in cndl:
          cndl.remove(target[0])

        rank1 = dict()
        rank2 = dict()
        self.saminfo.iscont=False
        self.datainfo.iscont=False
        self.datainfo.iscont = False
        for att in cndl:
                rank1[att] = [self.saminfo.CMI(att, target)]
        if istreatment!=[]:
            for att in cndl:
                  rank2[att] = [self.saminfo.CH(istreatment, att)]
            ranked_res1=dict_to_rank(rank1,0)
            ranked_res2=dict_to_rank(rank2, 0)
            rank = dict()
            for item in rank1.keys():
                if ranked_res1[item]>3:
                    ranked_res2[item]=1000
                elif ranked_res1[item]<=3:
                    ranked_res1[item]=0
            for item in rank1.keys():
                rank[item] = [ranked_res1[item] + ranked_res2[item]]
        else:
            rank=rank1
        cndl = top_kdict(rank, len(rank))
        if not istreatment:
            cndl.reverse()
        if debug:
           print(cndl)
        if whitelist:
          B = whitelist.copy()
        else:
          B=[]
        if debug:
            print(whitelist)
        reduc=len(self.features)-(len(cndl))
        if reduc>52:
            self.isshrink = True
            self.pre_com_view = pd.DataFrame(self.data.groupby(remove_dup(cndl +whitelist+ target+B)).size().reset_index(name="count"))
            self.pre_info = info.Info(self.pre_com_view, cont=True)
        else:
            self.isshrink=False
        discarded=[]

        for step in list(range(1, 3)):
            i = 0
            if step==5 and optimized:
                self.isshrink = False
                #self.pre_com_view = self.data
                discarded.clear()
            #    pass
                #self.pre_com_view= self.pre_com_view.groupby(B + target)['count'].sum().reset_index()
            while i < len(cndl):
                ''' 
                rank.clear()
                for att in cndl:
                    if att not in discarded:
                        if  att not in B:
                           rank[att] = [self.saminfo.CMI(att, target,B)]
                C=top_kdict(rank, len(rank))
                C.reverse()
                '''
                c = cndl[i]

                if flag==1:
                    if not self.isshrink:  # self.isshrink
                        self.isshrink = True
                        fes = diff(cndl, discarded)
                        self.pre_com_view = pd.DataFrame(
                            self.data.groupby(remove_dup(target + fes + whitelist)).size().reset_index(name="count"))

                    else:
                        print(remove_dup(fes + target + whitelist))
                        self.isshrink = True
                        self.pre_com_view = self.pre_com_view.groupby(remove_dup(fes + target + whitelist))[
                            'count'].sum().reset_index()
                    flag=0
                if c not in B:
                    if debug:
                        print("Testing: " + str(c))
                    if debug:
                        print('test started')
                    #print(self.datainfo.CMI(target, c, B))

                    x, I = self.CIT(target, c, B,pvalue=pvalue, method=method,
                                         debug=debug,fraction=fraction, coutious=coutious,ratio=ratio,loc_num_samples=loc_num_samples,
                                    num_samples=num_samples, maxmcs=maxmc)
                    if debug:
                        print(x,I)
                        print('test completed')
                    if x == 0:
                         B.insert(0, c)
                    else:
                       if optimized and step==2:
                               discarded.insert(0, c)
                               if len(discarded)  % alpha==0:
                                   print("Matrlized views")
                                   flag=1

                i = i + 1
                if debug:
                    print("Boundary: " + str(B))
        if debug:
            print('########Shrink started##########')
        #self.shrinkgroups=self.shrinkgroups.groupby(B+target).size()
        #self.shrinkinfo=info.Info(self.shrinkgroups,cont=True)
        #self.groups = pd.DataFrame(self.shrinkgroups.groupby(B+target).size().reset_index(name="count"))
        #self.df_size = self.groups['count'].sum()
        if optimized:
            print("Matrlized views")
            self.pre_com_view = pd.DataFrame(self.data.groupby(remove_dup(B + target)).size().reset_index(name="count"))
            if not self.isshrink:
                self.isshrink = True
                start=time.time()
                self.pre_com_view = pd.DataFrame(self.data.groupby(remove_dup(B + target)).size().reset_index(name="count"))
                end=time.time()
                print(end-start,'######################################')
            else:
                self.pre_com_view = self.pre_com_view.groupby(remove_dup(B + target))['count'].sum().reset_index()
        tmp = B.copy()
        discarded.clear()
        for b in tmp:
            if whitelist:
                if b in whitelist:
                    continue
            B.remove(b)
            if debug:
                print('test started')
            #print(self.datainfo.CMI(target,b,B))
            x, I = self.CIT(target, b, B, pvalue=pvalue, method=method,
                            debug=debug, fraction=fraction, coutious=coutious, ratio=ratio, loc_num_samples=loc_num_samples,
                            num_samples=num_samples,maxmcs=maxmc)
            if debug:
                print('test completed')
            if x == 0:
                B.insert(0, b)
            else:
                discarded.insert(0, c)
                if optimized:
                    if len(discarded) % alpha == 0:
                        print("Matrlized views")
                        self.pre_com_view = self.pre_com_view.groupby(remove_dup(B + target))['count'].sum().reset_index()
            if debug:
                print("Boundary: " + str(B))

        for item in B:
            self.rev_mbs[item] = target
        self.mbs[target[0]]=B.copy()
        endalg = time.time()
        #print("Boundary of  "+str(target[0]), str(B), ' ::::::: elapsed time:', endalg-startalg)
        return B, self.causes,endalg-startalg


    def grow_shrink2222(self, target, method,pvalue=0.05,
                    blacklist=None, whitelist=None, fraction=1, shfraction=1,
                    debug=False, coutious=True,ratio=1,loc_num_samples=100,num_samples=1000,istreatment=[]):

        if not target[0] in self.mbs.keys():
                    if target[0] in self.rev_mbs.keys():
                        whitelist=remove_dup(self.rev_mbs[target[0]]+whitelist)
                    print("Computing boundary of: ",target, ':::::: white list:', whitelist)
                    start=time.time()
                    cndl = copy.copy(self.features)
                    cndl = cndl.tolist()
                    if blacklist:
                        for item in blacklist:
                            if item in cndl:
                                cndl.remove(item)
                    # remove the target variables from the feature list
                    if isinstance(target, str):
                        target = [target]
                    for t in target:
                        if cndl.__contains__(t):
                            cndl.remove(t)
                    if whitelist:
                        for t in whitelist:
                            if cndl.__contains__(t):
                                cndl.remove(t)
                    ''' 
                    for att in cndl:
                            rank1[att] = [self.saminfo.CMI(att, target)]

                    if istreatment!=[]:
                        for att in cndl:
                              rank2[att] = [self.saminfo.CH(istreatment, att)]
                        ranked_res1=dict_to_rank(rank1,0)
                        ranked_res2=dict_to_rank(rank2, 0)
                        rank = dict()
                        for item in rank1.keys():
                            if ranked_res1[item]>3:
                                ranked_res2[item]=1000
                            elif ranked_res1[item]<=3:
                                ranked_res1[item]=0
                        for item in rank1.keys():
                            rank[item] = [ranked_res1[item] + ranked_res2[item]]
                    else:
                        rank=rank1
                    cndl = top_kdict(rank, len(rank))
                    if not istreatment:
                        cndl.reverse()
                    if debug:
                       print(cndl)
                    #cndl.reverse()
                    '''
                    if whitelist:
                      B = whitelist.copy()
                    else:
                      B=[]
                    if debug:
                        print(whitelist)
                    reduc=len(self.features)-(len(cndl))
                    self.pre_info=info.Info(self.data)
                    if reduc>=2:
                        self.isshrink = True
                        self.pre_com_view = pd.DataFrame(self.data.groupby(remove_dup(cndl +whitelist+ target+B)).size().reset_index(name="count"))
                        self.pre_info.data=self.pre_com_view
                        self.pre_info.iscont = True
                    else:
                        self.isshrink=False
                    discarded=[]
                    nsam = len(self.sample)

                    for step in list(range(1, 3)):
                        tmp = cndl.copy()
                        #    pass
                            #self.pre_com_view= self.pre_com_view.groupby(B + target)['count'].sum().reset_index()
                        rank = dict()
                        while len(tmp)>0:
                            rank.clear()
                            for att in tmp:
                                #rank[att] = [self.saminfo.CMI(target, att,B)]
                                x, I = self.CIT(att, target, B, pvalue=pvalue, method=method,
                                                debug=debug, fraction=fraction, coutious=coutious, ratio=ratio,
                                                loc_num_samples=loc_num_samples, num_samples=num_samples,
                                maxmc=maxmc)

                                #I = self.datainfo.CMI(target, att,B)
                                if x<pvalue:
                                    rank[att]=I
                            ranked_res1 = top_kdict(rank, 0)
                            ranked_res1.reverse()
                            #c = cndl[i]
                            if not ranked_res1:
                                break
                            c=ranked_res1[0]
                            tmp.remove(c)
                            x = 0
                            if c not in B:
                                if debug:
                                    print("Testing: " + str(c))
                                if debug:
                                    print('test started')
                                #print(self.datainfo.CMI(target, c, B))
                                #x, I = self.CIT(target, c, B, pvalue=pvalue, method=method,
                                #                     debug=debug,fraction=fraction, coutious=coutious,ratio=ratio,loc_num_samples=loc_num_samples,num_samples=num_samples)
                                if debug:
                                    print(x,I)
                                    print('test completed')
                                if x == 0:
                                     B.insert(0, c)
                                else:
                                   removed=True
                                   if   fraction<1 and I!=0 and self.flag:
                                      frac=1
                                      if coutious=='semi':
                                          frac==0.9
                                      if  coutious=='full':
                                          frac==1
                                      else:
                                          frac = fraction
                                      if coutious!='no':
                                          if debug:
                                                print("#########################I am here")
                                                print(B)
                                                print(c)
                                          x, I = self.CIT(target, c, B, pvalue=pvalue, method=method,
                                                            debug=debug, fraction=frac, coutious=coutious, ratio=ratio,
                                                            loc_num_samples=loc_num_samples, num_samples=num_samples)

                                      if x == 0:
                                            B.insert(0, c)
                                            removed = False

                                   if step == 2 and removed:
                                           discarded.insert(0, c)
                                           if len(discarded)  % len(self.features)/3==0:
                                               if not self.isshrink:  # self.isshrink
                                                   self.isshrink = True
                                                   fes = diff(cndl, discarded)
                                                   self.pre_com_view = pd.DataFrame(
                                                       self.data.groupby(remove_dup(target + fes+whitelist)).size().reset_index(name="count"))
                                                   self.pre_info.data = self.pre_com_view
                                                   self.pre_info.iscont = True
                                               else:
                                                   self.isshrink = True
                                                   self.pre_com_view = self.pre_com_view.groupby(remove_dup(fes+target+whitelist))[
                                                       'count'].sum().reset_index()
                                                   self.pre_info.data = self.pre_com_view
                                                   self.pre_info.iscont = True
                            if debug:
                                print("Boundary: " + str(B))
                    if debug:
                        print('########Shrink started##########')
                    #self.shrinkgroups=self.shrinkgroups.groupby(B+target).size()
                    #self.shrinkinfo=info.Info(self.shrinkgroups,cont=True)
                    #self.groups = pd.DataFrame(self.shrinkgroups.groupby(B+target).size().reset_index(name="count"))
                    #self.df_size = self.groups['count'].sum()
                    if not self.isshrink:
                        self.isshrink = True
                        self.pre_com_view = pd.DataFrame(self.data.groupby(remove_dup(B + target)).size().reset_index(name="count"))
                        self.pre_info.data=self.pre_com_view
                        self.pre_info.iscont = True
                    else:
                        pass
                        self.pre_com_view = self.pre_com_view.groupby(remove_dup(B + target))['count'].sum().reset_index()
                        self.pre_info.data=self.pre_com_view
                        self.pre_info.iscont = True

                    ''' 
                    if istreatment:
                        rank=dict()
                        for att in B:
                              rank[att] = [self.saminfo.CH(istreatment, att)]
                        B = top_kdict(rank, len(rank))
                    '''
                    tmp = B.copy()
                    for b in tmp:
                        if whitelist:
                            if b in whitelist:
                                continue
                        B.remove(b)
                        if debug:
                            print('test started')
                        #print(self.datainfo.CMI(target,b,B))
                        x, I = self.CIT(target, b, B, pvalue=pvalue, method=method,
                                        debug=debug, fraction=shfraction, coutious=coutious, ratio=ratio,loc_num_samples=loc_num_samples, num_samples=num_samples)
                        if debug:
                            print('test completed')
                        if x == 0:
                            B.insert(0, b)
                        else:
                            if fraction < 1 and I != 0 and self.flag:
                                frac = 1
                                if coutious == 'semi':
                                    frac == 0.5
                                if coutious == 'full':
                                    frac == 1
                                else:
                                    frac = fraction
                                if coutious != 'no':
                                    if debug:
                                        print("#########################I am here")
                                        print(B)
                                        print(c)
                                    x, I = self.CIT(target, b, B, pvalue=pvalue, method=method,
                                                            debug=debug, fraction=frac, coutious=coutious, ratio=ratio,
                                                            loc_num_samples=loc_num_samples, num_samples=num_samples)
                                if x == 0:
                                     B.insert(0, b)
                                else:

                                      self.pre_com_view = self.pre_com_view.groupby(remove_dup(B + target))['count'].sum().reset_index()
                                      self.pre_info.data = self.pre_com_view
                                      self.pre_info.iscont = True
                            else:

                                self.pre_com_view = self.pre_com_view.groupby(remove_dup(B + target))['count'].sum().reset_index()
                                self.pre_info.data = self.pre_com_view
                                self.pre_info.iscont = True

                    if debug:
                            print("Boundary: " + str(B))
                    end = time.time()
                    print("Boundary of  " + str(target[0]), str(B), ' ::::::: elapsed time:', end - start)
                    self.mbs[target[0]] = B.copy()
        else:
            B=self.mbs[target[0]]
        for item in B:
            if item in  self.rev_mbs.keys():
              self.rev_mbs[item] = self.rev_mbs[item]+target
            else:
              self.rev_mbs[item] = target
        #print(self.rev_mbs)
        return B, self.causes

    def learn_parents(self, target,target_boundary,pvalue=0.05, method='g2',
                                          ratio=0.1, fraction=0.1, shfraction=0.1, num_samples=1000,loc_num_samples=100,
                                          blacklist=[], whitelist=[], debug=False,
                                    coutious=False, deep=False,k=3, optimized=False,maxmc=100):
        if   target[0] in  self.childers.keys():
         for item in self.childers[target[0]]:
              if item in target_boundary:
                  target_boundary.remove(item)
        if target[0] in self.parents.keys():
           parents = self.parents[target[0]]
        else:
           parents=[]
        if blacklist:
            black = blacklist
        else:
            black = list()
        if len(target_boundary) < 2:
            return []
            #self.pre_info = info.Info(self.pre_com_view, cont=True)
        frac=fraction
        for x in target_boundary:
            if x in parents:
                continue
            indep_list, I = self.get_indep(x, target_boundary, pvalue=pvalue, method=method,
                                           debug=debug, coutious=coutious,fraction=frac, ratio=ratio,
                                           num_samples=num_samples,loc_num_samples=loc_num_samples,maxmc=maxmc)
            #print(x,indep_list)
            for indep_att in indep_list:
                if indep_att:
                    test_result, I = self.ptest(x, indep_att, target, pvalue=pvalue,
                                                method=method, fraction=1, coutious=coutious, ratio=ratio,
                                                num_samples=num_samples,loc_num_samples=loc_num_samples,maxmc=maxmc,
                                                debug=debug)
                    if test_result == 1:
                        if indep_att not in parents:
                            parents.insert(0, indep_att)
                        if x not in parents:
                            parents.insert(0, x)
        if debug:
            print('###########fast parents#########')
            print(parents)
            print('###########fast parents#########')
        if deep:
            for x in target_boundary:
                if x in parents:
                    continue
                if debug:
                    print('###########deep search#########')
                    print(x)
                    print('###########deep search#########')

                if x in self.rev_mbs.keys():
                    white=self.rev_mbs[x]
                #print(white)
                if isinstance(x,list):
                    vrtx=x[0]
                else:
                    vrtx=x
                if vrtx in self.mbs.keys():
                    boundary=self.mbs[vrtx]
                else:
                    boundary, causes,time = self.grow_shrink(x, pvalue=pvalue, method=method
                                      ,ratio=1, fraction=fraction, num_samples=num_samples,
                                      blacklist=black, whitelist=white, debug=debug, coutious=coutious,
                                      loc_num_samples=loc_num_samples, maxmc=maxmc,optimized=optimized)
                    if debug:
                        print('###########Boundary#########')
                        print(x,boundary)
                        print('###########Boundary#########')

                for item in boundary:
                    if item in self.rev_mbs.keys():
                       self.rev_mbs[item]=remove_dup(self.rev_mbs[item]+[x])
                    else:
                        self.rev_mbs[item] = [x]
                cov = boundary.copy()
                if target[0] in boundary:
                    cov.remove(target[0])
                if optimized:
                    self.pre_com_view = pd.DataFrame(
                    self.data.groupby(remove_dup(target_boundary+boundary + target)).size().reset_index(name="count"))
                    self.datainfo.data = self.pre_com_view
                    self.datainfo.iscont=True
                for y in target_boundary:
                    if x != y:
                        if y in boundary and y in cov:
                            cov.remove(y)
                        res=0

                        for i in list(range(0,min(k,len(cov)))):
                            #print(i)
                            can=findsubsets(cov, i)
                            for verc in can:
                                tmp = cov.copy()
                                for item in  verc:
                                   tmp.remove(item)
                                res, I = self.CIT(x, y, tmp, pvalue=pvalue, method=method,
                                            debug=debug, fraction=frac, coutious=coutious, ratio=ratio,
                                            num_samples=num_samples,loc_num_samples=loc_num_samples,
                                                  maxmcs =maxmc)

                                if res == 1:
                                    if fraction < 1 and I != 0 and method == 'fpermu':
                                        if coutious == 'semi':
                                            frac == 0.5
                                        if coutious == 'full':
                                            frac == 1
                                        if coutious != 'no':
                                            res, I = self.CIT(x, y, tmp, pvalue=pvalue, method=method,
                                                              debug=False, fraction=frac, coutious=coutious, ratio=ratio,
                                                              num_samples=num_samples, loc_num_samples=loc_num_samples,maxmcs=maxmc
                                                              )
                                #if res == 1:
                                #    break

                            test_result=0
                            if res == 1:
                                test_result, I = self.ptest(x, y, target+tmp, pvalue=pvalue,
                                                            method=method,
                                                            fraction=frac,
                                                            debug=debug,loc_num_samples=loc_num_samples,coutious=coutious,maxmc =maxmc)
                                # test_result = self.mi_test(self.data, x, y, target,
                                #                        debug=debug)
                            if test_result == 1:
                                if y not in parents:
                                    parents.insert(0, y)
                                if x not in parents:
                                    parents.insert(0, x)
                        self.datainfo.iscont=False
                        if y in boundary:
                            cov.insert(0, y)

        self.parents[target[0]]=parents
        for item in parents:
          if item in  self.childers.keys():
               self.childers[item]=self.childers[item]+target
          else:
              self.childers[item] =   target
        return parents
    def ptest(self,x,y,z, pvalue=0.05, method='fpermu',
                                           ratio=1, fraction=1, num_samples=1000,
                                           debug=False, coutious=False,loc_num_samples=100,maxmc=100):
        res, I = self.CIT(x,y, z, pvalue=pvalue, method=method,
                                    debug=debug, fraction=fraction, coutious=coutious, ratio=ratio,
                                    num_samples=num_samples,loc_num_samples=loc_num_samples,maxmcs=maxmc)
        if fraction < 1 and I != 0 and method == 'fpermu':
            if coutious == 'semi':
                fraction == 0.5
            if coutious == 'full':
                fraction == 1
            if coutious != 'no':
                res, I = self.CIT(x, y, z, pvalue=pvalue, method=method,
                                  debug=debug, fraction=fraction, coutious=coutious, ratio=ratio,
                                  num_samples=num_samples, loc_num_samples=loc_num_samples,maxmcs=maxmc)
        if debug:
            print('########')
            print(x)
            print(y)
            print(z)
            print(I)
            print('########')
        if res == 0:
            return 1, I  # c and b are parents of x
        else:
            return 0, I  # on or both of them are non-parents of x

    def mi_test(self, x, y, z,  alpha=0.0001, debug=False):
                a = info.Info.CMI(data,x, y)
                b = info.Info.CMI(data,x, y, z)
                if debug:
                    print('########')
                    print(x)
                    print(y)
                    print(a)
                    print(z)
                    print(b)
                    print('########')
                if b - a >= alpha:
                    return 1  # c and b are parents of x
                else:
                    return 0  # on or both of them are non-parents of x

    def get_parents(self, target, pvalue=0.05, method='adj_g2',
ratio=0.1, fraction=0.1, num_samples=1000, loc_num_samples=100,
                      blacklist=[], whitelist=[], debug=False,
                      coutious=False, IStime=False, maxmc=100,k=10,optimized=False,fullcheck=False):
        start=time.time()
        targetboundary, causes,timeeee = self.grow_shrink(target, pvalue=pvalue, method=method
                                      ,ratio=ratio, fraction=fraction, num_samples=num_samples,
                                      blacklist=blacklist, whitelist=whitelist, debug=debug, coutious=coutious,
                                      loc_num_samples=loc_num_samples,maxmc=maxmc,optimized=optimized)
        end=time.time()
        tdur=end-start
        self.isshrink=False
        # print("*****\n")
        # print(targetboundary, causes,timeeee)
        # print("\n*****")
        parents = self.learn_parents(target, target_boundary=targetboundary, pvalue=pvalue, method=method
                                      ,ratio=ratio, fraction=fraction, num_samples=num_samples,
                                      blacklist=blacklist, whitelist=whitelist, debug=debug, coutious=coutious,
                                      loc_num_samples=loc_num_samples, deep=True,k=k,maxmc=maxmc,optimized=optimized)

        # print("*****\n")
        # print(parents)
        # print("\n*****")
        #print(parents,'heree')
        if fullcheck==True and parents:
            if optimized:
                self.pre_com_view = pd.DataFrame(
                    self.data.groupby(remove_dup(targetboundary + parents + target)).size().reset_index(name="count"))
                self.datainfo.data = self.pre_com_view
                self.datainfo.iscont = True
            for par in parents:
                #boundary, causes, time2 = self.grow_shrink(par, pvalue=pvalue, method=method
                #                                          , ratio=1, fraction=fraction, num_samples=num_samples,
                #                                          blacklist=[], whitelist=[], debug=debug,
                #                                          coutious=coutious,
                #                                          loc_num_samples=loc_num_samples, maxmc=maxmc,
                #                                          optimized=optimized)


                #boundary.remove(item)
                boundary=targetboundary
                if target[0] in boundary:
                    boundary.remove(target[0])
                tretametboundary=targetboundary.copy()
                tretametboundary.remove(par)

                    #if len(cov)>len(boundary):
                    #    cov=boundary.copy()
                cov=tretametboundary
                for i in list(range(0, min(k, len(cov)))):
                        # print(i)
                        found=False
                        can = findsubsets(cov, i)
                        for verc in can:
                            tmp = cov.copy()
                            for item in verc:
                                tmp.remove(item)
                            res, I = self.CIT(target, par, tmp, pvalue=pvalue, method=method,
                                              debug=debug, fraction=fraction, coutious=coutious, ratio=ratio,
                                              num_samples=num_samples, loc_num_samples=loc_num_samples,
                                              maxmcs=maxmc)

                            if res==1:
                                parents.remove(par)
                                found=True
                                break
                                print('par removed')
                        if found==True:
                            break
                if found == True:
                        break
        #if parents:
            #if len(parents)<2:
            #    parents=[]
        if IStime:
            return targetboundary,parents,tdur
        else:
            return targetboundary, parents

    def get_indep(self,target,B, pvalue=0.05, method='fpermu',
                                           ratio=1, fraction=1, num_samples=1000,
                                           debug=False, coutious=False,loc_num_samples=100,maxmc=100):
        indep = []
        for c in B:
            if not c == target:
                x, I = self.CIT(target, c, pvalue=pvalue, method=method,
                                debug=debug, fraction=fraction, coutious=coutious,
                                ratio=ratio, num_samples=num_samples,loc_num_samples=loc_num_samples,
                                maxmcs=maxmc)
                if x == 1:
                    indep.insert(0, c)
        return indep, I





if __name__ == '__main__':
    black = ['fnlwgt', 'educationnum']
    #data = read_from_csv('/Users/babakmac/Documents/XDBData/berkeley.csv')
    #data-read_from_db('qexpriment718')
    #filename='dag5008' #10 m
    filename = 'dag84att10'  #
    data = read_from_db(filename)
    #print(len(data))
    #data.drop(data.columns[[0]], axis=1, inplace=True)  ## drop the first column
    #print(data.columns)
    detector = hypdb(data,1,cube=True,cubename='small10cubes')  # expricube12 cube 12  expricube10 small10cubes
    #detector = hypdb(data)
    #detector = hypdb(data, 1, database=True, tablename=filename)
    whitelist = []
    black = [""]  # ['fid', 'flightdate','origincityname', 'flightnum', 'tailnum','origincityname', 'depdelay', 'distance', 'arrdelayminutes', 'flights','yyear']
    rown = 100000
    start = time.time()
    print(len(data.index))
    target = ['b']
    fraction = 1
    method = 'g2'
    pvalue = 0.01
    num_samples = 1000
    loc_num_samples = 100
    debug = False
    coutious = 'yes'
    k=1000
    start=time.time()
    cov1, par1 = detector.get_parents(target, pvalue=pvalue, method=method
                                      ,ratio=1, fraction=fraction, num_samples=num_samples,
                                      blacklist=black, whitelist=whitelist, debug=False, coutious=coutious,
                                      loc_num_samples=loc_num_samples,maxmc=1000,fullcheck=True,optimized=False)

    end = time.time()
    print(cov1)
    print(par1)
    print('g test',detector.ngtest)
    print('p test',detector.nptest)
    print(end-start)


'''
Boundary: ['arrdelay', 'destcityname', 'yyear']
Boundary of  delayed ['arrdelay', 'destcityname', 'yyear']  ::::::: elapsed time: 8.304201126098633
['arrdelay', 'destcityname', 'yyear']
{}
g test 0
p test 42
8.304222106933594

Boundary of  carrier ['dest', 'yyear', 'crsdeptime', 'quarter']  ::::::: elapsed time: 0.7893519401550293
['dest', 'yyear', 'crsdeptime', 'quarter']
{}
g test 42
p test 0
0.7893698215484619

Boundary of  carrier ['dest', 'origincityname', 'yyear', 'crsdeptime', 'month']  ::::::: elapsed time: 5.857375860214233
['dest', 'origincityname', 'yyear', 'crsdeptime', 'month']
{}
g test 0
p test 42
5.857398986816406


['f', 'b', 'c', 'm', 'k'] heree
['m', 'f', 'k', 'b', 'c']
['f', 'b', 'c', 'm', 'k']
g test 643
p test 0
16.728121995925903


['m', 'f', 'k', 'b', 'c']
['b', 'c', 'f', 'm', 'k']
g test 112
p test 0
220.87081718444824  190

['a', 'f', 'e', 'i', 'g', 'd', 'b']
['f', 'e', 'b', 'a', 'd']
g test 694
p test 0
125.43286299705505

Boundary of  a ['b', 'c']  ::::::: elapsed time: 0.13115215301513672
[] heree
['c', 'a']
[]
g test 40
p test 0
2.0020599365234375

g test 40
p test 0
2.037764072418213

'''
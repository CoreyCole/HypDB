from pylab import *
import scipy.stats as stats
from  math import *
from hypdb.utils.read_data import read_from_csv
from hypdb.utils.util import get_distinct
from  math import *
import functools
import scipy.stats as stats
from pylab import *
from hypdb.utils.read_data import read_from_csv
from scipy.special import entr
import time
from scipy.special import entr
import pandas as pd
#from modules.statistics.hypothesis_test import *
import numpy_indexed as npi
from hypdb.utils.util import *
import numba
import os
import psycopg2
from hypdb.utils.read_data import *



class Info(object):
    def __init__(self,data,cont=False,cube=False, database=False,cubename='',tablename=''):
        #ent_vec={('2',): 0.6624251009169959, ('1',): 0.46486016281731624, ('2', '1'): 1.1260786508720364, ('3',): 0.6592182242592086, ('3', '1'): 1.1241257685185306, ('4',): 0.6360546499180026, ('4', '1'): 1.1003435629709328, ('5',): 0.6020225086355226, ('5', '1'): 1.066778439454538, ('6',): 0.3515538832282088, ('6', '1'): 0.7531694433216624, ('7',): 0.6928896290293375, ('7', '1'): 1.1577611828266903, ('8',): 0.5973876856921985, ('8', '1'): 1.0527193582646281, ('1', '6'): 0.7531694433216624, ('2', '6'): 1.0139696982518867, ('2', '1', '6'): 1.4120730374929606, ('3', '6'): 1.010787728813978, ('3', '1', '6'): 1.4124543349865937, ('4', '6'): 0.9763749940590742, ('4', '1', '6'): 1.377607314855839, ('5', '6'): 0.9535956722306906, ('5', '1', '6'): 1.3550341078445212, ('7', '6'): 1.044453826932347, ('7', '1', '6'): 1.4461518246665037, ('8', '6'): 0.9489757373207992, ('8', '1', '6'): 1.3330613804023321, ('1', '8', '6'): 1.3330613804023321, ('2', '6', '8'): 1.5053420706231968, ('1', '6', '8'): 1.3330613804023321, ('2', '1', '6', '8'): 1.8894889971454922, ('6', '8'): 0.9489757373207992, ('3', '6', '8'): 1.6080524788576307, ('3', '1', '6', '8'): 1.9917195167979074, ('4', '6', '8'): 1.5661962207734064, ('4', '1', '6', '8'): 1.9502606521258898, ('5', '6', '8'): 1.546116906690437, ('5', '1', '6', '8'): 1.930259646737758, ('7', '6', '8'): 1.641944200527769, ('7', '1', '6', '8'): 2.02603952718671, ('6', '6', '8'): 0.9489757373207992, ('6', '1', '6', '8'): 1.3330613804023321, ('8', '6', '8'): 0.9489757373207992, ('8', '1', '6', '8'): 1.3330613804023321, ('1', '2'): 1.1260786508720364, ('3', '2'): 1.320372770279152, ('4', '2'): 1.2580425508625563, ('5', '2'): 1.2465089624682792, ('6', '2'): 1.0139696982518867, ('7', '2'): 1.3553420762380817, ('8', '2'): 1.1537340355196224, ('2', '8'): 1.1537340355196224, ('1', '8'): 1.0527193582646281, ('1', '2', '8'): 1.6090254189461148, ('3', '8'): 1.2564293295425961, ('3', '2', '8'): 1.8117530514767837, ('4', '8'): 1.2263480316179498, ('4', '2', '8'): 1.749307571036738, ('5', '8'): 1.194466538243339, ('5', '2', '8'): 1.7373503005391828, ('6', '2', '8'): 1.5053420706231966, ('7', '8'): 1.2903246602572875, ('7', '2', '8'): 1.8463751613713952, ('2', '4', '8'): 1.749307571036738, ('1', '4', '8'): 1.6803620649909552, ('1', '2', '4', '8'): 2.203064258729314, ('3', '4', '8'): 1.8854165336241393, ('3', '2', '4', '8'): 2.4072843499901393, ('5', '4', '8'): 1.8213666160499338, ('5', '2', '4', '8'): 2.3328723309557033, ('6', '4', '8'): 1.5661962207734066, ('6', '2', '4', '8'): 2.086917179319415, ('7', '4', '8'): 1.919349557425984, ('7', '2', '4', '8'): 2.4420008152734223, ('2', '5', '4', '8'): 2.332872330955704, ('1', '4', '5', '8'): 2.2755011137581382, ('2', '4', '5', '8'): 2.3328723309557033, ('1', '2', '4', '5', '8'): 2.786891378220611, ('4', '5', '8'): 1.8213666160499338, ('3', '4', '5', '8'): 2.434161474023957, ('3', '2', '4', '5', '8'): 2.94563414616066, ('6', '4', '5', '8'): 2.161395705281423, ('6', '2', '4', '5', '8'): 2.670724041364189, ('7', '4', '5', '8'): 2.5142254070918186, ('7', '2', '4', '5', '8'): 3.025511999458211, ('2', '6', '4', '5', '8'): 2.670724041364189, ('1', '6', '4', '5', '8'): 2.545576314356484, ('1', '2', '6', '4', '5', '8'): 3.054862674958047, ('3', '6', '4', '5', '8'): 2.7742733410984988, ('3', '2', '6', '4', '5', '8'): 3.28366212213697, ('7', '6', '4', '5', '8'): 2.8544809407341774, ('7', '2', '6', '4', '5', '8'): 3.3633318653176407, ('4', '6', '4', '5', '8'): 2.1613957052814228, ('4', '2', '6', '4', '5', '8'): 2.670724041364189, ('5', '6', '4', '5', '8'): 2.1613957052814228, ('5', '2', '6', '4', '5', '8'): 2.6707240413641884, ('6', '6', '4', '5', '8'): 2.161395705281423, ('6', '2', '6', '4', '5', '8'): 2.670724041364189, ('8', '6', '4', '5', '8'): 2.161395705281423, ('8', '2', '6', '4', '5', '8'): 2.6707240413641893, ('1', '7'): 1.1577611828266903, ('2', '7'): 1.3553420762380815, ('3', '7'): 1.352053161532893, ('4', '7'): 1.3289907659391305, ('5', '7'): 1.294708461426641, ('6', '7'): 1.044453826932347, ('8', '7'): 1.2903246602572873}
        self.data = data
        self.iscont = False
        self.iscube=cube
        self.database = database
        self.columns=list(data.columns)
        self.cubename=cubename
        self.tablename=tablename
        if cube or database:
            self.iscube=cube
            myConnection = psycopg2.connect(host='localhost', user='bsalimi', password='1', dbname='postgres')
            # conn.cursor will return a cursor object, you can use this cursor to perform queries
            self.cursor = myConnection.cursor()
        if cont==True:
            self.df_size = self.data['count'].sum()
            self.iscont=True
        else:
            self.df_size = len(self.data.index)
        self.distint=dict()
        self.ent_vec = dict()
        self.numberofentropies=0
        self.entropycalculation=0

    def CH(self, X, Y=None,base=e):
        if isinstance(X, str):
            X = tuple([X])
        elif isinstance(X, list):
            X = tuple(X)
        if isinstance(Y, str):
            Y = tuple([Y])
        elif isinstance(Y, list):
            Y = tuple(Y)
        if Y:
                XY = X + Y
                HY = self.entropy(Y,base)
                HXY = self.entropy(XY,base)
                return HXY - HY
        else:
            self.entropy(X)

    def CMI(self, X, Y, Z=[], base=e,normilized=False):

            if isinstance(X,str):
                X=tuple([X])
            elif  isinstance(X,list):
                X = tuple(X)
            if isinstance(Y,str):
                Y=tuple([Y])
            elif  isinstance(Y,list):
                Y = tuple(Y)

            if len(Z)!=0:
                if isinstance(Z, str):
                    Z = tuple([Z])
                elif isinstance(Z, list):
                    Z = tuple(Z)
                XZ = X  + Z
                YZ = Y  + Z
                XYZ = X  + Y  + Z
                HXZ=self.entropy(XZ, base=base)
                HYZ=self.entropy(YZ, base=base)
                HXYZ=self.entropy(XYZ, base=base)
                HZ=self.entropy(Z, base=base)
                I = HXZ + HYZ - HXYZ - HZ
                if normilized:
                    if HXZ and HYZ:
                      I = I*(log(self.df_size)/log(e)) #*min(HXZ , HYZ))
                      I = I / sqrt(HXZ * HYZ)
                      #I = I * (log(n) / log(e))
                    else:
                      I=0
                else:
                    I=HXZ+HYZ-HXYZ-HZ
                return I
            else:
                XY = X  + Y
                HX = self.entropy(X,base=base)
                HY = self.entropy(Y,base=base)
                HXY = self.entropy(XY,base=base)
                if normilized:
                    I = HX + HY - HXY
                    if HX and HY:
                      I = I/min(HX,HY)
                      #I = I * (log(n) / log(e)) #* min(HX, HY))
                    else:
                      I=0
                else:
                    I=HX + HY - HXY
                return I

    @functools.lru_cache(maxsize=None)
    def get_distinct(self,att):
            # print('#################')
            # print(att)
            # print(type(att))
            ##data=np.array(data[att])
            # dtype = data.dtype.descr * ncols
            # struct = data.view(dtype)
            if att in self.distint:
                return self.distint[att]
            else:
                if self.iscont:
                    freqlist = self.data.groupby(att).size()
                else:
                    freqlist = self.data.groupby(att).size()
            # uniq = np.unique(struct)
            # uniq = uniq.view(data.dtype).reshape(-1, ncols)
            # states=np.unique(data[att])
            # df= data[att].drop_duplicates()
            # print(freqlist)
            return  len(freqlist)

    def gb_count(self,df,X):
            df=df[X]
            hasht=dict()
            for index, row in df.iterrows():
                t=row[0]
                if t in hasht.keys():
                    hasht[t]+=1
                else:
                    hasht[t] = 1
            return list(hasht.values())

    @functools.lru_cache(maxsize=None)
    def entropy(self,X,base=e):
        ent=0
        #X=remove_dup(X)
        string=''
        if self.database==True:
            for item in X:
                    if string:
                        string = string + ',' + str(item)
                    else:
                        string = string + str(item)

            query = 'SELECT count(*) FROM {} group by {}'.format(self.tablename, string)
            print(query)
            self.cursor.execute(query)
            iout = self.cursor.fetchall()
            freqlist = []
            for item in iout:
                freqlist.insert(0, item[0])
            self.distint[X] = len(freqlist)
            probs = np.divide(freqlist, sum(freqlist))
            ent = entr(probs)
            # h=self.get_distinct(X)
            ent = np.sum(ent)
            self.ent_vec[X] = ent
            # cashe[X[0]]=ent
            end = time.time()
            self.numberofentropies = self.numberofentropies + 1
            return ent

        if self.iscube:
                for item in self.columns:
                    if item=='count':
                        continue
                    if item in X:
                        if string:
                          string=string+' and '+str(item)+'  is not null '
                        else:
                          string = string + str(item) + ' is not null '
                    else:
                         if string:
                           string=string+' and '+str(item)+'  is  null '
                         else:
                            string = string + str(item) + ' is  null '

                query = 'SELECT count FROM {} where {}'.format(self.cubename,string)
                print(query)
                self.cursor.execute(query)
                iout=self.cursor.fetchall()
                freqlist=[]
                for item in iout:
                    freqlist.insert(0,item[0])
                self.distint[X] = len(freqlist)
                probs = np.divide(freqlist, sum(freqlist))
                ent = entr(probs)
                    # h=self.get_distinct(X)
                ent = np.sum(ent)
                self.ent_vec[X] = ent
                    # cashe[X[0]]=ent
                end = time.time()
                self.numberofentropies = self.numberofentropies + 1
                return ent
        start=time.time()
        if isinstance(X, str):
            X = tuple([X])
        elif isinstance(X, list):
            X = tuple(X)
        if X in self.ent_vec.keys():
            return self.ent_vec[X]
            ##print(self.iscont)
        else:
            if self.iscont==False:
                 start = time.time()
                 freqlist =  self.data.groupby(X).size()
                 #print(freqlist)
                 end=time.time()
                 #print(X,end-start)
             #freqlist = self.gb_count(self.data,X).size()
            else:
                 freqlist = self.data.groupby(X)['count'].sum()
            self.distint[X]=len(freqlist)
            probs =np.divide(freqlist,self.df_size)
            ent=entr(probs)
            #h=self.get_distinct(X)
            ent=np.sum(ent)
            self.ent_vec[X]=ent
            #cashe[X[0]]=ent
        end=time.time()
        self.entropycalculation=self.entropycalculation+end-start
        self.numberofentropies=self.numberofentropies+1
        return ent

'''
def entropy(data,X,base=e):
    # return entropy of a set of attributs of a dataframe
        dis = get_distinct(data, X)
        n = len(data.index)
        freqlist =  data.groupby(X).size()
        return stats.entropy(freqlist,base=base) #+(dis-1)/(2*n)
 '''

if __name__ == '__main__':
    data=read_from_csv('/Users/babakmac/Documents/XDBData/lungcancer.csv')


    #c = inf.get_distinct(tuple(['dayofweek', 'dayofmonth', 'monthh', 'yyear', 'crsdeptime', 'origin', 'dest', 'deptime', 'arrtime', 'arrdelay']))
    #data = read_from_db('dag8new')
    inf=Info(data)
    start=time.time()
    s1 = inf.CMI(['peer_pressure'], ['anxiety'])
    s=inf.CMI(['peer_pressure'],['anxiety'],['smoking'])
    end = time.time()
    print('ffff',end-start)
    print('MUTUALLLL',s,s1)

    print(end-start)
    print(s)

    #data = read_from_csv('/Users/babakmac/Documents/XDBData/NEWDATA/DAG2cube_1_2_5000 .csv')

    inf=Info(data,database=True,tablename='dag8new')
    start=time.time()
    s=inf.entropy(tuple(['a','b']))
    end = time.time()
    print('sss',end-start)
    #Y=ci_mi(X,3,34000,0.99)
    #print(Y)
#0.01770305633544922
#24685




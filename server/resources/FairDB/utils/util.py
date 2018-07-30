import numpy as np
import pandas as pd

def list2string(list):
    return  str(list).replace('[]', '').replace('[', '').replace(']', '').replace("'", '').replace(" ","")

def dict_to_rank(x,loc):
        sorted_x = reversed(sorted(x.items(), key=lambda e: e[1][loc]))
        out_dict = {}
        old=-1
        i=0
        for idx, (key, item) in enumerate(sorted_x):
            if old==item[loc]:
                out_dict[key] = i
            else:
                out_dict[key] = i+1
                i=i+1
            old=item[loc]
        #print(sorted(out_dict.items(), key=lambda x: x[1]))
        return out_dict

def top_kdict(dic,k):
    kv_list=sorted(dic.items(), key=lambda x: x[1])
    kv_list=kv_list[-k:]
    kv_list=dict(kv_list)
    return list(kv_list.keys())


def unique_rows(a):
    a = np.ascontiguousarray(a)
    unique_a = np.unique(a.view([('', a.dtype)]*a.shape[1]))
    return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))

def remove_dup(lst):
    lst=set(lst)
    return list(lst)

def get_distinct(data,att):
    #print('#################')
    #print(att)
    #print(type(att))
    ##data=np.array(data[att])
    #dtype = data.dtype.descr * ncols
    #struct = data.view(dtype)
    freqlist = data.groupby(att).size()
    #uniq = np.unique(struct)
    #uniq = uniq.view(data.dtype).reshape(-1, ncols)
    #states=np.unique(data[att])
    #df= data[att].drop_duplicates()
    #print(freqlist)
    return len(freqlist)

def printTable(myDict, colList=None):
   """ Pretty print a list of dictionaries (myDict) as a dynamically sized table.
   If column names (colList) aren't specified, they will show in random order.
   Author: Thierry Husson - Use it as you want but don't blame me.
   """
   if not colList: colList = list(myDict[0].keys() if myDict else [])
   myList = [colList] # 1st row = header
   for item in myDict: myList.append([str(item[col] or '') for col in colList])
   colSize = [max(map(len,col)) for col in zip(*myList)]
   formatStr = ' | '.join(["{{:<{}}}".format(i) for i in colSize])
   myList.insert(1, ['-' * i for i in colSize]) # Seperating line
   for item in myList: print(formatStr.format(*item))


def bining(df,att,bins,group_names=False):
    df[att] = pd.cut(df[att], bins, labels=group_names)
    return df
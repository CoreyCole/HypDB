from pylab import *
from scipy.stats import spearmanr
from utils.read_data import read_from_csv
import modules.infotheo.info_theo as info


def get_high_entropy_atts(data, start=0.3, end=0.4, steps=0.01, cut=0.0001, alpha=0.01, debug=False):
    # treatment="'"+treatment+"'"
    samplesizez = []
    dic = dict()
    black = []
    white = []
    basesample = data.sample(frac=0.3, replace=False)
    features=data.columns.values
    size = len(data.index)
    while start <= end:
        start = start + steps
        sample = basesample.sample(frac=start, replace=False)
        samplesizez.insert(0, (len(sample.index)))
        inf=info.Info(sample)
        for col in features:
            if col in dic:
                list = dic[col]
                list.insert(0, inf.entropy(col, size))
                dic[col] = list
            else:
                dic[col] = [inf.entropy(col, size)]

    for col in features:
        if not any(dic[col]):
            continue
        rho, pval1 = spearmanr(samplesizez, dic[col])
        if debug == True:
            print(col)
            print(pval1)
            print("#####")
            plt.plot(dic[col])
            plt.show()
        if pval1 <= alpha:
            black.insert(0, col)
        else:
            white.insert(0, col)
    # self.features=np.array(white)
    return black

def get_fds(data, targets, cut=0.0001, debug=False, blacklist=None):
          fds=list()
          features = data.columns.values
          size = len(data.index)
          inf = info.Info(data)
          if not blacklist:
              blacklist=[]
          for att in targets:
              for col in features:
                  if  col not in att and col not in blacklist:
                      x = inf.CH(att, col)
                      if debug:
                           print('#############')
                           print(col)
                           print(x)
                      if x <= cut:
                          fds.insert(0, col)
                          if debug:
                              print('Functional depedancy detected'+ str(col))
                              print('#############')
                      y = inf.CH(col,att)
                      if debug:
                           print('#############')
                           print(col)
                           print(y)
                      if y <= cut:
                          fds.insert(0, col)
                          if debug:
                              print('Functional depedancy detected'+ str(col))
                              print('#############')
          return fds

if __name__ == '__main__':
    data=read_from_csv('/Users/babakmac/Documents/XDBData/binadult.csv')
    treatment = ['sex']
    outcome = ['income']
    X=get_high_entropy_atts(data)
    X=get_fds(data,treatment, debug=True)
    print(X)
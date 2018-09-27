from modules.core.XDB import *

if __name__ == '__main__':

    treatment = ['carrier']
    outcome = ['carrier']
    table = 'qtable3level'
    detector = discovery(table, treatment, outcome)
    X = detector.naive_groupby()
    print(X)
    answers=X[0]['mean'].values
    print(answers)
    boundary = [ 'yyear', 'quarter', 'dayofweek', 'month', 'originwac']
    scovarite = []
    print(boundary)
    odist=var(answers)
    for i in range(0, len(boundary)):
        candidate = boundary[i]
        scovarite.insert(0, candidate)
        print(scovarite)
        res = detector.adjusted_groupby(scovarite)
        if res==None:
          print('no-overlap')
          continue
        second = res[0]['mean'].values
        overlap = res[2]
        ndis = var(second)
        if ndis-odist < 0 :
            #print(first)
            ##print(second)
            print(ndis)
            odist = ndis
        else:
            if  scovarite.__contains__(candidate):
                   scovarite.remove(candidate)
            print('removed')
            print(candidate)
            print(scovarite)

    adj2 = scovarite
    print(scovarite)
    print(res)
    print(odist)

def query_to_list(answers): # convert a query answer to a list
    list=[]
    print(answers)
    entery=''
    for item in answers:
        item=str(item[0])
        if type(item)==str:
         entery=item.replace("(", "").replace(")", "").replace(',', "")
        if entery:
            list.insert(0,entery)
    return list

    def generategroupby(self):
        cursor = self.myConnection.cursor()
        query = 'SELECT * FROM {}'.format(self.relation)
        cursor.execute(query)
        res=cursor.fetchall()
        return [res,self.features]


class RandomQueryGenarator(object):
     def __init__(self,treatment,atts,table,force,treatmentlevel):
         self.myConnection = psycopg2.connect(host='localhost', user='bsalimi', password='1', dbname='postgres')
         # conn.cursor will return a cursor object, you can use this cursor to perform queries
         cursor = self.myConnection.cursor()
         # execute our Query
         self.treatmentlevel=treatmentlevel
         self.forceoverlap=force
         self.treatment=treatment
         self.statevalues={}
         self.table=table
         self.table=table
         atts.insert(0,treatment)
         # this eventually contain all states of the attributes in atts
         for att in atts:
            query = 'SELECT distinct {} FROM {}'.format(att, self.table)
            tmp = pd.read_sql_query(query, con=self.myConnection)
            if len(tmp.values)>0:
             self.statevalues[att]= tmp.values


     def creataradomtable(self,name,p=20): # generate a random query wrt a tretament att
         # conn.cursor will return a cursor object, you can use this cursor to perform queries
         randomattval={}
         for att in self.statevalues.keys():
              x = self.statevalues[att]
              x=x.tolist()
              if att!=self.treatment and att!=self.forceoverlap:
                  n = randint(int(len(x)/2)+1, len(x))
                  randomattval[att]=sample(x,n)

         randomattval[self.treatment] = sample(self.statevalues[self.treatment].tolist(), self.treatmentlevel)
         x = randomattval[self.treatment]
         s = str(x).replace('[', '(')
         s = str(s).replace(']', ')')
         query = 'select {}  from {} where {} in {} group by {} having ' \
              'count(distinct {})={}'.format(self.forceoverlap, self.table, self.treatment, s, self.forceoverlap,
                                            self.treatment,self.treatmentlevel)
         print(query)
         tmp = pd.read_sql_query(query, con=self.myConnection)
         res = tmp.values
         if len(res)>1:
             n = randint(2, len(res))
             if n>15:
                 n=randint(4, 10)
             randomattval[self.forceoverlap] = sample(res.tolist(),n)
         else:
             return 0
         wherecluse=''
         counter=1
         for att in randomattval.keys():
               x=randomattval[att]
               s=str(x).replace('[','(')
               s=str(s).replace(']', ')')
               if counter==len(randomattval.keys()):
                 wherecluse=wherecluse+'{} in {}'.format(att,s)
               else:
                 wherecluse = wherecluse + '{} in {} AND '.format(att,s)
               counter=counter+1
         #q1='DROP table if exists q{}; '.format(name)
         curs = self.myConnection.cursor()
         try:
         # curs.execute("DROP TABLE if exists q{}").format(name)
         #curs.execute(q1)
             q2='Create materialized view q{} as (Select * from {} where {})'.format(name, self.table, wherecluse)
             curs.execute(q2)
             self.myConnection.commit()
             print(q2)
         except Exception as inst:
             print(type(inst))  # the exception instance
             print(inst.args)  # arguments stored in .args
             print(inst)
         #q1 = 'drop materialized view if exists  sampleq{} cascade'.format(name)

         try:
             q3= 'Create materialized view sampleq{} as (Select * from q{} TABLESAMPLE BERNOULLI ({}))'.format(name,name,p)
             curs.execute(q3)
             self.myConnection.commit()
         except Exception as inst:
             print(type(inst))  # the exception instance
             print(inst.args)  # arguments stored in .args
             print(inst)
         try:
             q0 = 'select count(distinct {}) from q{}'.format(self.treatment,name)
             res=curs.execute(q0)
             res=curs.fetchall()
         except Exception as inst:
             print(type(inst))  # the exception instance
             print(inst.args)  # arguments stored in .args
             print(inst)
         if res[0][0]!=2:
             return 0
         else:
             return ['q'+str(name),q2]  #return the name of a table and the query used to create it


     def deletetable(self,name):
         curs = self.myConnection.cursor()
         q1="DROP materialized view if exists {} cascade".format(name)
         q2 = "DROP materialized view if exists sampleq{} cascade".format(name)
         curs.execute(q1)
         curs.execute(q2)
         self.myConnection.commit()
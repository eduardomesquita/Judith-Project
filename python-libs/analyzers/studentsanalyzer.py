import time
from datetime import datetime
from abstract.analyzerabstract import *

current_dir =  '/'.join( sys.path[0].split('/')[:-1] )
sys.path.append(current_dir + '/utils/')
import replaceutils as replace_utils


class StudentsAnalyzer(  AnalyzerAbstract ):

    def __init__(self):
        AnalyzerAbstract.__init__(self)
        setattr(self, 'raw_data', {})
        setattr(self, 'users_status_name', {})
      
   
    def get_raw_data(self, projection):
        self.raw_data = {}
        for user_name in self.users_status_name.keys():
     
             self.raw_data[user_name] = []
             for cursor in self.twitter_db.get_raw_data_users( user_name=user_name,
                                                               projection=projection):
                 for bjson in list(cursor):
                    location = replace_utils.remove_non_ascii_chars( bjson['user']['location'] )
                    location =  replace_utils.get_location( location )
                    if location is not None:
                       self.raw_data[user_name].append({'location': location,
                                                      'created_at' : bjson['created_at']})


    def __sum__(self, key, **kargs):
        if kargs.has_key( key ):
            kargs[ key ] += 1
        else:
            kargs[ key ] = 1
        return kargs

    def __set_status__(self, **kargs):

        for user in  kargs.keys():
            student, possible = 0, 0
            if kargs[ user ].has_key('POSSIVEL'):
                possible = int(kargs[user]['POSSIVEL'])
            if kargs[ user ].has_key('ESTUDANTE'):
                student = int(kargs[user]['ESTUDANTE'])

            if possible >= student:
                self.users_status_name[user] = 'possible'
            else:
                self.users_status_name[user] = 'student'

        self.users_status_name['name'] = 'users_status_name'
        self.analyzer_db.save_cache_data( **self.users_status_name)



    def __count_user_by_status__(self):
        status_users = {}
        for bjson in self.analyzer_db.get_raw_data_students():
            user_name, status, count=bjson['userName'],bjson['statusStudents'],bjson['count']
            if not status_users.has_key( user_name ):
               status_users[user_name] = {}
            status_users[user_name][status] = count

        self.__set_status__( **status_users )

    def get_status(self, user_name):
        return self.users_status_name[ user_name ] 


    def __aggregation_location__(self):

        aggretation = {}
        for user, list_bjson in self.raw_data.iteritems():
            aggretation[user] = { 'location': {},
                                  'status_users' : self.get_status(user_name=user) }
            for bjson in list_bjson:
                if bjson.has_key('location'):
                    location = bjson['location'].replace('.', '').upper()
                    
                    if len(location) >  3:
                        if aggretation[user]['location'].has_key( location ):
                           aggretation[user]['location'][location] += 1
                        else:
                            aggretation[user]['location'][location] = 1

            if aggretation[user]['location'] == {}:
               del aggretation[user]

        aggretation['name'] = 'user_status_location'
        self.analyzer_db.save_cache_data( **aggretation ) 
        

    def __aggregation_creat_at__(self, fmt = '%H:%M:%S'):
     
        aggretation = {}
        for user, list_bjson in self.raw_data.iteritems():
            aggretation[user] = { 'created_tweet_at': {'year':{},
                                                       'month':{},
                                                       'day':{},
                                                       'hour':{},
                                                       'minute':{}},
                                  'status_users' : self.get_status( user ) }

            for bjson in list_bjson:
               if bjson.has_key('created_at'):
                    ts = time.strftime('%Y-%m-%d %H:%M:%S',
                        time.strptime(bjson['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))

                    (data_str, time_str) = ts.split(' ')
                    (y, mo, d) = data_str.split('-')
                    (h, mi, s) = time_str.split(':')
                    
                    aggretation[user]['created_tweet_at']['year'] = self.__sum__(y, **aggretation[user]['created_tweet_at']['year'])
                    aggretation[user]['created_tweet_at']['month'] = self.__sum__(mo, **aggretation[user]['created_tweet_at']['month'])
                    aggretation[user]['created_tweet_at']['day'] = self.__sum__(d, **aggretation[user]['created_tweet_at']['day'])
                    aggretation[user]['created_tweet_at']['hour'] = self.__sum__(h, **aggretation[user]['created_tweet_at']['hour'])
                    aggretation[user]['created_tweet_at']['minute'] = self.__sum__(mi, **aggretation[user]['created_tweet_at']['minute'])

    
        aggretation['name'] = 'user_status_created_at'
        self.analyzer_db.save_cache_data( **aggretation ) 
               
    def init(self):

        print 'start cache StudentsAnalyzer..'

        ##name1  users_status_name 
        ##name2 user_status_location
        ##name3 user_status_created_at

        self.analyzer_db.remove_cache(name='users_status_name')
        self.analyzer_db.remove_cache(name='user_status_location')
        self.analyzer_db.remove_cache(name='user_status_created_at')
        
        self.__count_user_by_status__()
        self.get_raw_data({'_id':0})

        self.__aggregation_location__()
        self.__aggregation_creat_at__()
        
        print 'Fim cache StudentsAnalyzer..'
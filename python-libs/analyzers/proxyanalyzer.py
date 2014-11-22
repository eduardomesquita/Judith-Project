from studentsanalyzer import *
from tweetanalyzer import *
from groupstudentsanalyzer import *
from configdb import *
from interfaces.analyzerinterface import AnalyzerInterface
import threading
from analyzerdb import AnalyzerDB


class AnalyzerProxy( AnalyzerInterface ):

    def __init__(self):
        setattr(self,'students_analyzer', StudentsAnalyzer())
        setattr(self,'tweet_analyzer', TweetAnalyzer())
        setattr(self, 'group_students_analyzer', GroupStudentsAnalyzer())
        setattr(self,'config_db', ConfigDB());
        setattr(self, 'analyzer_db', AnalyzerDB())

    def start(self):
        try:

            t1 = threading.Thread(name='Thread-1', target=self.students_analyzer.init)
            t2 = threading.Thread(name='Thread-2', target=self.tweet_analyzer.init)
            t3 = threading.Thread(name='Thread-3', target=self.group_students_analyzer.init)

            t1.start()
            t2.start()
            t3.start()

        except Exception as e:
            print "Erro: nao foi possivel iniciar thread. %s" % e
    

    def is_dust(self):
        if len(list(self.config_db.is_dust_analyzed())) > 0:
            print 'inicando analize'
            self.start()
            self.config_db.update_dust_analyzer()

    def get_analysis(self, key):
        self.is_dust()
        return list( self.analyzer_db.get_cache_analysis( key ) )

    def get_students_count_tweet(self, status):
        self.is_dust()
        return list( self.analyzer_db.get_students_count_tweet( status ) )
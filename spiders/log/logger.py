#-------------logger.py
import  sys,os
import  logging
import  datetime
from    logging import handlers

class Logger(object):

    #----------------------------------------------------------------------------
    def __init__(self,file_path,log_type=1,log_level=logging.INFO):
        
        parentDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        parentDir = parentDir + "\\..\\log\\grap\\" + "{}\\{}\\".format(datetime.datetime.now().year,datetime.datetime.now().month) 
        #self.file_path = "./run/"
        self.file_path = parentDir
        self.file_name = ""
        self.config(file_path,log_type,log_level)
    
    #---------------------------------------------------------------------------
    def logger(self):
        logger = logging.getLogger(self.file_name)
        return logger    
    
    def show(self,str):
        log          = logging.getLogger(self.file_name)
        log.info(str)
    
    #-----------------------------------------------------------------------------------------
    def config(self,file_path,log_type,log_level=logging.INFO):

        IsStream        = False
        log             = None
        log_path        = " "
        str_formate     = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
        str_date        = "%Y-%m-%d %H:%M:%S"
        isMakeDir       = [False,True][log_type>0]
        isFileHandler   = [False,True][log_type>0 ]
        isStreamHandler = [False,True][log_type>1 ]
        isConsole       = [False,True][log_type==0 ]
        
        #create file
        if isMakeDir:
            log_dir   = self.file_path + file_path
            nowTime   = datetime.datetime.now().strftime('%Y-%m-%d')
            log_path  = log_dir + f'/{nowTime}.log'
            self.file_name = log_path
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

        #
        if not isConsole:
            log           = logging.getLogger(log_path)
        else:
            log           = logging.getLogger( )
        #
        if isFileHandler:
            if not log.handlers:
                file_handler = logging.FileHandler(filename=log_path,encoding = 'utf-8', mode = 'a')
                str_formats   = logging.Formatter(str_formate )
                file_handler.setFormatter(str_formats )
                file_handler.setLevel(log_level)
                log.addHandler(file_handler)
                IsStream = True
        
        #output to console
        if isStreamHandler:
           # if not log.handlers:
            if IsStream:
                stream_handler = logging.StreamHandler()
                str_formats    = logging.Formatter(str_formate )
                stream_handler.setFormatter(str_formats)
                stream_handler.setLevel(log_level)
            
                #log.setLevel(log_level )
                log.addHandler(stream_handler)

        #console
        if isConsole:
            if not log.handlers:
                stream_handler = logging.StreamHandler()
                str_formats    = logging.Formatter(str_formate )
                stream_handler.setFormatter(str_formats)
                stream_handler.setLevel(log_level)
                
                log.setLevel(log_level )
                log.addHandler(stream_handler)

        log.setLevel(log_level )      
        





    

    

    
  

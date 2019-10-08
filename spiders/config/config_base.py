#config_base.py
import configparser
 
class Config(object):
    def __init__(self, filename):
        self.filename = filename
        self.config = configparser.ConfigParser()
        self.config.read(self.filename)
    
    def read_baidu_tieba(self):
        self.sub_thread_count = self.config.get("baidu_tieba", "sub_thread_count")

        self.grapInfo_url     = self.config.get("baidu_tieba", "grapInfo_url")
        self.grapInfo_compoundword = self.config.get("baidu_tieba", "grapInfo_compoundword")

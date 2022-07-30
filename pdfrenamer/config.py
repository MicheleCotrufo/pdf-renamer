import configparser
import os
import logging


class config():
    #Default values for all parameters. If the file settings.ini is absent, these values are used
    __params={'verbose'   :   True,
            'format' : "{YYYY} - {Jabbr} - {A3etal} - {T}",
            'max_length_authors' : 80,
            'max_length_filename' : 250,
            'max_words_title' : 5,
            'check_subfolders' : False,
            'case' : ''
            }
    __setters = __params.keys()


    @staticmethod
    def update_params(new_params):
        config.__params.update(new_params)

    @staticmethod
    def get(name):
        return config.__params[name]

    @staticmethod
    def set(name, value):
        if name in config.__setters:
             config.__params[name] = value
        else:
            raise NameError("Name not accepted in set() method")
        #Here we define additional actions to perform when specific parameters are modified
        if name == 'verbose':
            # We change the logger verbosity for this package and and also for pdf2bib and pdf2doi
            if value: loglevel = logging.INFO
            else: loglevel = logging.CRITICAL
            logger = logging.getLogger("pdf-renamer")
            logger.setLevel(level=loglevel)
            try:
                logger = logging.getLogger("pdf2bib")
                logger.setLevel(level=loglevel)
                logger = logging.getLogger("pdf2doi")
                logger.setLevel(level=loglevel)
            except:
                pass

    @staticmethod
    def ReadParamsINIfile():
        '''
        Reads the parameters stored in the file settings.ini, and stores them in the dict self.params
        If the .ini file does not exist, it creates it with the default values.
        '''
        path_current_directory = os.path.dirname(__file__)
        path_config_file = os.path.join(path_current_directory, 'settings.ini')
        if not(os.path.exists(path_config_file)):
            config.WriteParamsINIfile()
        else:
            config_object = configparser.ConfigParser()
            config_object.optionxform = str
            config_object.read(path_config_file)
            config.__params.update(dict(config_object['DEFAULT']))
            config.ConvertParamsToBool()
            config.ConvertParamsToNumb()

    @staticmethod
    def ConvertParamsToBool():
        for key,val in config.__params.items():
            if isinstance(val, str):
                if val.lower() == 'true':
                    config.__params[key]=True
                if val.lower() == 'false':
                    config.__params[key]=False

    @staticmethod
    def ConvertParamsToNumb():
        for key,val in config.__params.items():
            if isinstance(val, str) and val.lstrip("-").isdigit(): #the lstrip("-") part makes sure that also strings like '-1' are recognized as valid numbers
                config.__params[key]=int(val)
    @staticmethod
    def print():
        '''
        Prints all settings
        '''
        for key,val in config.__params.items():
            print(key + " : " + str(val) + ' ('+type(val).__name__+')')

    @staticmethod
    def WriteParamsINIfile():
        '''
        Writes the parameters currently stored in in the dict self.params into the file settings.ini
        '''
        path_current_directory = os.path.dirname(__file__)
        path_config_file = os.path.join(path_current_directory, 'settings.ini')
        config_object = configparser.ConfigParser()
        config_object.optionxform = str
        config_object['DEFAULT'] = config.__params
        with open(path_config_file, 'w') as configfile: #Write them on file
            config_object.write(configfile)


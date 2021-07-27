import configparser
import os

class config():
    params={'verbose'   :   True,
            'format' : "{YYYY} - {Jabbr} - {A3etal} - {T}",
            'max_length_authors' : 80,
            'max_length_filename' : 250,
            'numb_results_google_search' : 6
            }
        
    def __init__(self):
        self.ReadParamsINIfile()

    def update_params(self,new_params):
        self.params.update(new_params)

    def ReadParamsINIfile(self):
        '''
        Reads the parameters stored in the file settings.ini, and stores them in the dict self.params
        '''
        path_current_directory = os.path.dirname(__file__)
        path_config_file = os.path.join(path_current_directory, 'settings.ini')
        config = configparser.ConfigParser()
        config.read(path_config_file)
        self.params.update(dict(config['DEFAULT']))
        self.ConvertParamsToNumb()

    def ConvertParamsToNumb(self):
        for key,val in self.params.items():
            if val.isdigit():
                self.params[key]=int(val)


    def WriteParamsINIfile(self):
        '''
        Writes the parameters currently stored in in the dict self.params into the file settings.ini
        '''
        params_dict = {key: str(value) for key, value in (self.params).items()} #Make sure that each value of the dict is converted to a string
        path_current_directory = os.path.dirname(__file__)
        path_config_file = os.path.join(path_current_directory, 'settings.ini')
        config = configparser.ConfigParser()
        #config.read(path_config_file)   #Read the current values of the parameters in settings.ini
        #paramsOLD = config['DEFAULT']
        #paramsOLD.update(params_dict) #Update the new values
        config['DEFAULT'] = self.params
        with open(path_config_file, 'w') as configfile: #Write them on file
            config.write(configfile)

Config = config()
#Config.params['max_length_filename'] = 500
#Config.WriteParamsINIfile()
#params_dict = ReadParamsINIfile() #Read the current value of parameters when config.py gets first loaded (which happens when the whole module gets imported)
#for key,val in params_dict.items():
#    if val.isdigit():
#        exec(key + '=int(val)')
#    else:
#        exec(key + '=val')



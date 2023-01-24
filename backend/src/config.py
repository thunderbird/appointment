import configparser

def config(option, section='DEFAULT'):
  """get global app configuration"""
  conf = configparser.ConfigParser()
  conf.read('src/appointment.ini')
  return conf[section][option]

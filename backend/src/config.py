import configparser

def config(option, section='DEFAULT'):
  """get global app configuration"""
  conf = configparser.ConfigParser()
  conf.read('backend/src/appointment.ini')
  return conf[section][option]

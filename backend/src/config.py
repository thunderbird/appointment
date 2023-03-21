from dotenv import dotenv_values, find_dotenv

def config(key):
  """get backend app configuration"""
  env = dotenv_values(find_dotenv())
  return env.get(key)

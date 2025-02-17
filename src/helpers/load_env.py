import yaml

config_path = 'config.yaml'

def db_env(env):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config['database'][env]

def folder_env():
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config['folders']
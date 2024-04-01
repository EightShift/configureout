import json


class BaseConfig():
    def __init__(self, config):
        self.__config = config
        
        for key, value in self.__config.items():
            setattr(self, key, BaseConfig(value) if type(value) == dict else value)


class Config(BaseConfig):
    def __init__(self, config_file):
        self.__file = config_file
        
        self._load_config()

    def _load_config(self):
        with open(self.__file, "r", encoding="utf-8") as config:
            config = json.loads(config.read())

            super().__init__(config)


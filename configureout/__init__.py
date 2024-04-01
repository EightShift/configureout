import json


class BaseConfig():
    def __init__(self, config):
        self.__config = config
        
        for key, value in self.__config.items():
            setattr(self, key, BaseConfig(value) if type(value) == dict else value)


class Config(BaseConfig):
    def __init__(self, config_file, encoding='utf-8'):
        self.__file = config_file

        self._load_config(encoding)

    def _load_config(self, encoding):
        with open(self.__file, "r", encoding=encoding) as config_file:
            config = json.loads(config_file.read())

            super().__init__(config)
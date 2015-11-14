

from os.path import join, isdir, isfile
from Code.PluginInterface.PluginConfig import PluginConfig

class BadPluginException(Exception):
    """ Exception which is raised when a plugin failed to load """
    pass

class VirtualPlugin(object):

    """ This is a virtual plugin which emulates the functionality of a 
    Pipeline Plugin outside of the pipeline """

    def __init__(self):
        pass

    def load(self, plugin_id):
        """ Loads the virtual plugin from a given id """
        self._plugin_id = plugin_id
        self._plugin_pth = join("../../Plugins/", self._plugin_id)
        self._config_pth = join(self._plugin_pth, "config.yaml")

        if not isfile(self._config_pth):
            raise BadPluginException("Missing file " + self._config_pth)

        self._load_config()

    def _load_config(self):
        """ Loads the plugin config """

        self._config = PluginConfig()
        self._config.load(self._config_pth)

    def consume_overrides(self, overrides):
        """ Removes all keys from the dictionary which belong to this
        plugin and applies them to the settings """
        self._config.consume_overrides(self.get_id(), overrides)

    def get_name(self):
        """ Returns the name of the virtual plugin """
        return self._config.get_name()

    def get_config(self):
        """ Returns the PluginConfig of the virtual plugin """
        return self._config

    def get_id(self):
        """ Returns the ID of the virtual plugin """
        return self._plugin_id
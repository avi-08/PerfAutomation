# Contains class for accessing all configuration files

import os
import copy
import re
import pprint


class Settings:
    """
    class to provide configurations as object across the framework
    """

    def __init__(self):
        pass

    def _eval_param(self, param):
        """ Helper function for expansion of references to vsperf parameters
        """
        if isinstance(param, list) or isinstance(param, tuple):
            tmp_list = []
            for item in param:
                tmp_list.append(self._eval_param(item))
            return tmp_list
        elif isinstance(param, dict):
            tmp_dict = {}
            for (key, value) in param.items():
                tmp_dict[key] = self._eval_param(value)
            return tmp_dict
        else:
            return param

    def getValue(self, attr):
        """Return a settings item value
        """
        if attr in self.__dict__:
            default_value = getattr(self, attr)
            return self._eval_param(default_value)
        else:
            raise AttributeError("%r object has no attribute %r" %
                                 (self.__class__, attr))

    def __setattr__(self, name, value):
        """Set a value
        """
        # skip non-settings. this should exclude built-ins amongst others
        if not name.isupper():
            return

        # we can assume all uppercase keys are valid settings
        super(Settings, self).__setattr__(name, value)

    def setValue(self, name, value):
        """Set a value
        """
        if name is not None and value is not None:
            super(Settings, self).__setattr__(name, value)

    def resetValue(self, attr):
        """If parameter was overridden by TEST_PARAMS, then it will
           be set to its original value.
        """
        if attr in self.__dict__['TEST_PARAMS']:
            self.__dict__['TEST_PARAMS'].pop(attr)

    def __str__(self):
        """Provide settings as a human-readable string.

        This can be useful for debug.

        Returns:
            A human-readable string.
        """
        tmp_dict = {}
        for key in self.__dict__:
            tmp_dict[key] = self.getValue(key)

        return pprint.pformat(tmp_dict)

    def load_from_file(self, path):
        """Update ``settings`` with values found in module at ``path``.
        """
        import json
        data = json.load(open(path))
        if data.items():
            for key in data:
                setattr(self, key, data[key])

    def load_from_dir(self, dir_path):
        """Update ``settings`` with contents of the .conf files at ``path``.

        Each file must be named Nfilename.conf, where N is a single or
        multi-digit decimal number.  The files are loaded in ascending order of
        N - so if a configuration item exists in more that one file the setting
        in the file with the largest value of N takes precedence.

        :param dir_path: The full path to the dir from which to load the .conf
            files.

        :returns: None
        """
        regex = re.compile("^([a-z]?).*.json$")

        # get full file path to all files & dirs in dir_path
        file_paths = os.listdir(dir_path)
        file_paths = [os.path.join(dir_path, x) for x in file_paths]

        # filter to get only those that are a files, with a leading
        # digit and end in '.conf'
        file_paths = [x for x in file_paths if os.path.isfile(x) and
                      regex.search(os.path.basename(x))]

        # load settings from each file in turn
        for filepath in file_paths:
            self.load_from_file(filepath)

    def load_from_dict(self, conf):
        """
        Update ``settings`` with values found in ``conf``.

        Unlike the other loaders, this is case insensitive.
        """
        for key in conf:
            if conf[key] is not None:
                if isinstance(conf[key], dict):
                    # recursively update dict items, e.g. TEST_PARAMS
                    setattr(self, key.upper(),
                            merge_spec(getattr(self, key.upper()), conf[key]))
                else:
                    setattr(self, key.upper(), conf[key])

    def restore_from_dict(self, conf):
        """
        Restore ``settings`` with values found in ``conf``.

        Method will drop all configuration options and restore their
        values from conf dictionary
        """
        self.__dict__.clear()
        tmp_conf = copy.deepcopy(conf)
        for key in tmp_conf:
            self.setValue(key, tmp_conf[key])

    def load_from_env(self):
        """
        Update ``settings`` with values found in the environment.
        """
        for key in os.environ:
            setattr(self, key, os.environ[key])


settings = Settings()


def get_test_param(key, default=None):
    """Retrieve value for test param ``key`` if available.

    :param key: Key to retrieve from test params.
    :param default: Default to return if key not found.

    :returns: Value for ``key`` if found, else ``default``.
    """
    test_params = settings.getValue('TEST_PARAMS')
    return test_params.get(key, default) if test_params else default


def merge_spec(orig, new):
    """Merges ``new`` dict with ``orig`` dict, and returns orig.

    This takes into account nested dictionaries. Example:

        >>> old = {'foo': 1, 'bar': {'foo': 2, 'bar': 3}}
        >>> new = {'foo': 6, 'bar': {'foo': 7}}
        >>> merge_spec(old, new)
        {'foo': 6, 'bar': {'foo': 7, 'bar': 3}}

    You'll notice that ``bar.bar`` is not removed. This is the desired result.
    """
    for key in orig:
        if key not in new:
            continue

        # Not allowing derived dictionary types for now
        # pylint: disable=unidiomatic-typecheck
        if type(orig[key]) == dict:
            orig[key] = merge_spec(orig[key], new[key])
        else:
            orig[key] = new[key]

    for key in new:
        if key not in orig:
            orig[key] = new[key]

    return orig

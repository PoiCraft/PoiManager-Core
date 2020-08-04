import os

from database.ConfigHelper import get_config


class PropertiesLoader:

    def __init__(self, no_bds=False):
        self.prop_path = os.path.join(
            get_config('bedrock_server_root'),
            get_config('bedrock_server_properties')
        )
        if no_bds:
            prop_str = ''
        else:
            prop_str = open(self.prop_path).read()
        self.prop = self.loadProp(prop_str)
        self.prop_old = self.exportProp(self.prop)
        self.prop_in_file = self.exportProp(self.prop)

    def if_edited(self):
        return self.exportProp(self.prop) != self.prop_old

    def if_saved(self):
        return self.exportProp(self.prop) == self.prop_in_file

    def edit_prop(self, key: str, value: str):
        self.prop[key] = value
        return self.if_edited()

    def get_prop(self, key: str):
        return self.prop.get(key, None)

    def save(self):
        with open(self.prop_path, 'w') as prop:
            prop.write(self.exportProp(self.prop))
            prop.close()
        self.prop_in_file = self.exportProp(self.prop)

    # noinspection PyMethodMayBeStatic
    def loadProp(self, prop_str: str) -> dict:
        prop_map = {}
        prop_list = prop_str.splitlines()
        for prop_w in prop_list:
            if len(prop_w) == 0:
                continue
            if prop_w[0] == '#' or prop_w[0] == ' ':
                continue
            prop_d = prop_w.split('=')
            if len(prop_d) < 2:
                continue
            prop_map[prop_d[0]] = prop_d[1]
        return prop_map

    # noinspection PyMethodMayBeStatic
    def exportProp(self, prop_map: dict) -> str:
        prop_list = []
        for k in prop_map:
            prop_list.append(k + '=' + prop_map[k])
        prop_str = '\n'.join(prop_list)
        return prop_str

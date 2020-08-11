import re

import yaml

from database import BdsLogger
from database.ConfigHelper import get_config


class BdsFilter:

    def __init__(self):
        self.bds_filter_enable = get_config('bds_filter_enable') == 'true'
        self.bds_filter_type = get_config('bds_filter_type')
        self.bds_filter_filters = get_config('bds_filter_filters')

        self.filter_sort_match = {}
        self.filter_sort_in = {}
        self.filter_ignore_match = []
        self.filter_ignore_in = []
        self.filter_sort_other = ''

        self.filters = yaml.safe_load(
            open(self.bds_filter_filters).read()
        ).get(self.bds_filter_type, None)
        if self.filters is None:
            self.bds_filter_enable = False
            BdsLogger.put_log('filter', 'Unable to load Filters, disabled.')

        if self.bds_filter_enable:
            self.filter_sort_other = self.filters.get('sort', {}).get('other', 'result')
            self.filter_sort_match = self.filters.get('sort', {}).get('match', {})
            self.filter_sort_in = self.filters.get('sort', {}).get('in', {})
            self.filter_ignore_match = self.filters.get('ignore', {}).get('match', [])
            self.filter_ignore_in = self.filters.get('ignore', {}).get('in', [])

    def if_ignore(self, log: str) -> bool:
        if not self.bds_filter_enable:
            return False
        for v in self.filter_ignore_match:
            if re.match(v, log):
                return True
        for v in self.filter_ignore_in:
            if v in log:
                return True
        return False

    def sort_log(self, log: str) -> str:
        if not self.bds_filter_enable:
            return 'bds'
        for v in self.filter_sort_match:
            if re.match(self.filter_sort_match[v], log):
                return v
        for v in self.filter_sort_in:
            if self.filter_sort_in[v] in log:
                return v
        return self.filter_sort_other

import os
import csv
import gdal
import numpy as np

from collections import defaultdict


# @@@ - assert for data format?
class SSURGO(dict):
    def __init__(self, path):
        super(SSURGO, self).__init__()
        self.path = path
        self.states = sorted({d.upper() for d in os.listdir(self.path) if len(d) == 2})

    def __getattr__(self, item):
        if item not in dir(self):
            if item in self.states:
                return self[item]
            else:
                print("State \"{}\" not in SSURGO".format(item))
        else:
            return getattr(self, item)

    def __getitem__(self, state):
        if state not in self.keys():
            state = state.upper()
            state_path = os.path.join(self.path, state)
            if not os.path.isdir(state_path):
                print("{} was not found in the specified SSURGO dataset")
                return
            else:
                val = State(state, state_path)
        else:
            val = self[state]
        return val

    def __iter__(self):
        for s in sorted(self.states):
            yield self[s]

    # TBD
    def states_containing(self, map_unit_or_component):
        pass


class State:
    def __init__(self, state, path):
        self.name = state
        self.path = path
        self.grid = os.path.join(path, state)

        # Variables that are generated upon being called
        self.ds = None
        self._array = None
        self._components = None
        self._horizons = None
        self._map_units = None
        self._headings = None
        self._tables = None

    def __getattr__(self, item):
        if item not in dir(self):
            if item in self.tables.keys():
                return self.tables[item]
            else:
                print("Table {} not in {}".format(item, self.name))
        else:
            return getattr(self, item)

    def __repr__(self):
        return "SSURGO Data for {}".format(self.name)

    @property
    def array(self):
        if not self._array:
            if not self.ds:
                self.ds = gdal.Open(self.grid)
            self._array = np.array(self.ds.GetRasterBand(1).ReadAsArray())
            self._array[self._array < 0] = 0
        return self._array

    @property
    def components(self):
        if not self._components:
            self._components = self.tables['component'].map_components("mukey", "cokey", "comppct_r")
        return self._components

    @property
    def headings(self):
        """
        Match up all possible attributes with the tables in which they're located, and whether the attribute matches
        with a map unit, component, or horizon
        :return: {heading: [table1, table2,..], ...}
        """
        if not self._headings:
            self._headings = defaultdict(list)
            for table in self.tables.values():
                for heading in table.headings:
                    self._headings[heading].append(table)
        return self._headings

    @property
    def horizons(self):
        if not self._horizons:
            self._horizons = self.tables['chorizon'].map_components("cokey", "chkey")
        return self._horizons

    @property
    def map_units(self):
        if not self._map_units:
            self._map_units = self.components.keys()
        return self._map_units

    @property
    def tables(self):
        if not self._tables:
            self._tables = {}
            for f in os.listdir(self.path):
                name, ext = os.path.splitext(f)
                if ext == ".csv":
                    path = os.path.join(self.path, f)
                    self._tables[name] = Table(path, name, self)
        return self._tables


class Table:

    def __init__(self, path, name, state):
        self.path = path
        self.name = name
        self.state = state

        self._headings = []
        self._index = None

    def __getattr__(self, item):
        if item not in dir(self):
            if item in self.headings:
                return self.read_field(item)
            else:
                print("Field {} not in {}".format(item, self.name))
        else:
            return getattr(self, item)

    @property
    def index(self):
        if not self._index:
            self._index = IndexType()
            types = []
            for key in ("mukey", "cokey", "chkey"):
                if key in self.headings:
                    types.append(key)
            if len(types) > 1:
                print("Unable to identify an index for table {}".format(self.name))
            elif len(types) == 1:
                self._index = IndexType(types.pop())
        return self._index

    @property
    def headings(self):
        if not self._headings:
            with open(self.path) as f:
                self._headings = f.readline().strip().split(",")
        return self._headings

    @property
    def indexed(self):
        if self.index.type == "not indexed":
            return False
        else:
            return True

    def map_components(self, super_key, sub_key, third_key=None):
        out_dict = defaultdict(list)
        with open(self.path) as f:
            reader = csv.DictReader(f)
            for line in reader:
                super_val = int(line[super_key])
                sub_val = int(line[sub_key])
                if third_key:
                    out_dict[super_val].append((sub_val, line[third_key]))
                else:
                    out_dict[super_val].append(sub_val)
        return out_dict

    def read_field(self, field_name):
        with open(self.path) as f:
            reader = csv.DictReader(f, has_header=True)
            if field_name in reader.fieldnames and self.index in reader.fieldnames:
                return {r[self.index]: r[field_name] for r in reader}
            else:
                print("Unable to match field \"{}\" to index \"{}\" in table \"{}\"".format(
                    field_name, self.index, self.name))

class IndexType:
    def __init__(self, index_field="N/A"):
        types = {"mukey": "map unit",
                 "cokey": "component",
                 "chkey": "horizon",
                 "N/A": "not indexed"}.get(self.field)
        self.field = index_field
        if index_field not in types:
            print("Invalid index field {}".format(index_field))
            self.index_field = "N/A"
        self.type = types[index_field]


def map_unit_average(data, component_map):
    """
    Converts component level data into map unit level data by taking an area-weighted average
    :param data:
    :param component_map:
    :return:
    """
    out_data = dict.fromkeys(component_map.keys(), 0.0)
    for map_unit, component in component_map.items():
        component_id, component_pct = component
        component_value = float(data.get(component_id, 0.0))
        proportional_value = (component_pct / 100.0) * component_value
        out_data += proportional_value
    return out_data


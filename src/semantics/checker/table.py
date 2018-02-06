from src.semantics.semantics import DataStructure
from src.semantics.symbols.symbol_table import Package
import pickle


# table manager - controls table for analysis
class TableManager:
    def __init__(self, table):
        self.table = table
        self.pos = 0
        self.prevPos = []

    def find(self, elem):
        layers = self.prevPos
        level = self.table
        while True:
            top = False
            for item in layers:
                level = level[item]
            if level == self.table:
                top = True
            for var in level:
                if isinstance(var, Package):
                    if var.used:
                        pass
                    elif var.alias == elem.name:
                        return self.unpack(var).find(elem)
                if self.compare(var, elem):
                    return var
            else:
                if top:
                    return False
                layers.pop()

    def unpack(self, pkg):
        table = pickle.load(pkg.dep_dir).symbol_table

        class OpenedPackage:
            def __init__(self):
                self.table = table

            def find(self, elem):
                pass

        return OpenedPackage()

    # compares identifier w/ member from table
    @staticmethod
    def compare(var1, var2):
        def raw_compare(var1=var1, var2=var2):
            if var1.name == var2.name and var1.group == var2.group and var1.is_instance == var2.is_instance:
                return True

        if raw_compare():
            return True
        if var2.data_structure in [DataStructure.STRUCT, DataStructure.INTERFACE, DataStructure.TYPE, DataStructure.MODULE]:
            for item in var2.members:
                if raw_compare(var1, item):
                    return True
        return False

    def descend(self):
        self.prevPos.append(self.pos)
        self.pos = 0

    def ascend(self):
        self.pos = self.prevPos[-1]


def has_modifier(name, var):
    pass


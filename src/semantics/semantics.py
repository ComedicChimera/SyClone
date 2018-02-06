from enum import Enum


# all data structures
class DataStructure(Enum):
    STRUCT = 0
    INTERFACE = 1
    TYPE = 2
    VARIABLE = 3
    CONSTANT = 4
    MODULE = 5
    FUNCTION = 6


class DataTypes(Enum):
    INT = 0
    FLOAT = 1
    BOOL = 2
    STRING = 3
    CHAR = 4
    BYTE = 5
    COMPLEX = 6


class DataType:
    def __init__(self):
        self.data_type = DataTypes(DataTypes.INT)
        self.pointer = []


class ListType(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.element_type = DataType()


class DictType(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.key_type = DataType()
        self.value_type = DataType()


# main semantic class for ALL variables
class Variable:
    def __init__(self):
        self.name = ""
        self.group = []
        self.modifiers = []
        self.data_structure = DataStructure(DataStructure.VARIABLE)
        self.is_instance = False


# main semantic class for standard variables and constants
class TypedVariable(Variable):
    def __init__(self):
        Variable.__init__(self)
        self.data_type = DataType()
        self.initializer = None


# main semantic class for all data structures ie. type and interface
class Structure(Variable):
    def __init__(self):
        Variable.__init__(self)
        # sub members
        self.members = []


# main function semantic class
class Function(Variable):
    def __init__(self):
        Variable.__init__(self)
        self.return_type = None
        self.parameters = []
        self.data_structure = DataStructure.FUNCTION
        self.is_async = False
        self.is_constructor = False
        self.group_inherits = []
        self.code = []


class ModuleTypes(Enum):
    ACTIVE = 0
    PASSIVE = 1
    AWAIT = 2


# main module semantic class
class Module(Variable):
    def __init__(self):
        Variable.__init__(self)
        self.data_structure = DataStructure.MODULE
        self.mod_type = ModuleTypes.ACTIVE
        self.inherit = []
        self.constructor = []
        self.members = []


# main return/semantic storage object
class SemanticConstruct:
    def __init__(self, symbol_table, ast):
        self.symbol_table = symbol_table
        self.ast = ast

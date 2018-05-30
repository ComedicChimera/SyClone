import syc.icg.types as types
from syc.icg.action_tree import Literal


# used to check if a static cast is valid
def static_cast(dt, obj):
    # check item
    def check_elem(tp, elem):
        # if it is possible to perform static cast
        if isinstance(elem, Literal):
            if not static_cast(tp.element_type, elem):
                return False
        else:
            # otherwise default to dynamic cast
            if not dynamic_cast(tp.element_type, elem.data_type):
                return False
        return True

    # if dynamic cast is valid, static cast is valid
    if dynamic_cast(dt, obj.data_type):
        return True
    # since dynamic cast would detect explicitly equal types, this checks for static cast lists
    elif type(dt) == type(obj.data_type):
        # check lists and arrays
        if isinstance(dt, types.ListType) or isinstance(dt, types.ArrayType):
            for item in obj.value:
                if not check_elem(dt.element_type, item):
                    return False
            return True
        # check dictionary
        elif isinstance(dt, types.DictType):
            for k, v in obj.value.items():
                if not check_elem(dt.key_type, k) or not check_elem(dt.value_type, v):
                    return False
            return True

    # check normal types
    if isinstance(dt, types.DataType):
        # byte array conversions
        if isinstance(obj.data_type, types.ArrayType) and isinstance(obj.data_type.element_type, types.DataType):
            if obj.data_type.element_type.data_type == types.DataTypes.BYTE and dt.pointers == 0:
                array_len = len(obj.value)
                size = types.get_size(types.DataTypes.CHAR) if dt.data_type == types.DataTypes.STRING else types.get_size(dt.data_type)
                if size % array_len == 0 or array_len < size:
                    return True
            return False
        # if object has pointers or it is not a normal data type, it is invalid
        if obj.data_type.pointers > 0 or not isinstance(obj.data_type, types.DataType):
            return False
        # single byte conversions
        elif obj.data_type.data_type == types.DataTypes.BYTE:
            size = types.get_size(types.DataTypes.CHAR) if dt.data_type == types.DataTypes.STRING else types.get_size(dt.data_type)
            if int(obj.value[2:], 16) // 128 <= size:
                return True
        # float literal to int
        elif dt.data_type == types.DataTypes.INT:
            if obj.data_type.data_type == types.DataTypes.FLOAT and float(obj.value).is_integer():
                return True
        # char conversions
        elif dt.data_type == types.DataTypes.CHAR:
            # string literal to char
            # < 4 because of enclosing quotations on string
            if obj.data_type.data_type == types.DataTypes.STRING and len(list(obj.value)) < 4:
                return True
            # integer literal to char
            elif obj.data_type.data_type == types.DataTypes.INT and 0 < int(obj.value) < 256:
                return True
        # int to byte
        elif dt.data_type == types.DataTypes.BYTE:
            if obj.data_type.data_type == types.DataTypes.INT and 0 < int(obj.value) < 256:
                return True
    # default to false
    return False


# used to check if a dynamic cast (using no Literal value, is explicitly valid)
def dynamic_cast(dt1, dt2):
    if types.coerce(dt1, dt2):
        return True
    # coerce catches explicitly equal types, so this is a valid test to assume complex data types
    if type(dt1) == type(dt2):
        # check lists and arrays
        if isinstance(dt1, types.ListType) or isinstance(dt1, types.ArrayType):
            return dynamic_cast(dt1.element_type, dt2.element_type)
        # check dictionaries
        elif isinstance(dt1, types.DictType):
            return dynamic_cast(dt1.key_type, dt2.key_type) and dynamic_cast(dt1.value_type, dt2.value_type)
        # check functions
        elif isinstance(dt1, types.Function):
            # check for pointer mismatch
            if dt1.pointers != dt2.pointers:
                return False
            # check for generator mismatch
            elif dt1.generator != dt2.generator:
                return False
            # check for parameter mismatch
            elif dt1.parameters != dt2.parameters:
                return False
            # check for unconvertable return types
            elif not dynamic_cast(dt1.return_type, dt2.return_type):
                return False
            # check to ensure that dt1 is dominant in asynchronous
            elif not dt1.async and dt2.async:
                return False
            return True

    # list / array type conversion
    elif (isinstance(dt1, types.ListType) or isinstance(dt1, types.ArrayType)) and (isinstance(dt2, types.ListType) or isinstance(dt2, types.ArrayType)):
        # make sure elements can be coerced
        if dynamic_cast(dt1.element_type, dt2.element_type):
            return True
    # dynamic type type checking
    if isinstance(dt1, types.DataType):
        if not isinstance(dt2, types.DataType):
            return False
        elif types.get_size(dt1.data_type) >= types.get_size(dt2.data_type):
            return True
    # default to false
    return False


# perform value cast (no assignment)
def value_cast(value):
    pass

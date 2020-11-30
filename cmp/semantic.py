import itertools as itt
from collections import OrderedDict


class SemanticError(Exception):
    @property
    def text(self):
        return self.args[0]

class Attribute:
    def __init__(self, name, typex, idx=None):
        self.name = name
        self.type = typex
        self.idx = idx

    def __str__(self):
        return f'[attrib] {self.name} : {self.type.name};'

    def __repr__(self):
        return str(self)

class Method:
    def __init__(self, name, param_names, param_types, return_type, param_idx, ridx=None):
        self.name = name
        self.param_names = param_names
        self.param_types = param_types
        self.param_idx = param_idx
        self.return_type = return_type
        self.ridx = ridx

    def __str__(self):
        params = ', '.join(f'{n}:{t.name}' for n,t in zip(self.param_names, self.param_types))
        return f'[method] {self.name}({params}): {self.return_type.name};'

    def __eq__(self, other):
        return other.name == self.name and \
            other.return_type == self.return_type and \
            other.param_types == self.param_types

class Type:
    def __init__(self, name:str):
        self.name = name
        self.attributes = []
        self.methods = []
        self.parent = None

    def set_parent(self, parent):
        if self.parent is not None:
            raise SemanticError(f'Parent type is already set for {self.name}.')
        self.parent = parent

    def get_attribute(self, name:str):
        try:
            return next(attr for attr in self.attributes if attr.name == name)
        except StopIteration:
            if self.parent is None:
                raise SemanticError(f'Attribute "{name}" is not defined in {self.name}.')
            try:
                return self.parent.get_attribute(name)
            except SemanticError:
                raise SemanticError(f'Attribute "{name}" is not defined in {self.name}.')

    def define_attribute(self, name:str, typex):
        try:
            self.get_attribute(name)
        except SemanticError:
            attribute = Attribute(name, typex)
            self.attributes.append(attribute)
            return attribute
        else:
            raise SemanticError(f'Attribute "{name}" is already defined in {self.name}.')

    def get_method(self, name:str):
        try:
            return next(method for method in self.methods if method.name == name)
        except StopIteration:
            if self.parent is None:
                raise SemanticError(f'Method "{name}" is not defined in {self.name}.')
            try:
                return self.parent.get_method(name)
            except SemanticError:
                raise SemanticError(f'Method "{name}" is not defined in {self.name}.')

    def define_method(self, name:str, param_names:list, param_types:list, return_type, param_idx:list, ridx=None):
        if name in (method.name for method in self.methods):
            raise SemanticError(f'Method "{name}" already defined in {self.name}')

        method = Method(name, param_names, param_types, return_type, param_idx, ridx)
        self.methods.append(method)
        return method

    def all_attributes(self, clean=True):
        plain = OrderedDict() if self.parent is None else self.parent.all_attributes(False)
        for attr in self.attributes:
            plain[attr.name] = (attr, self)
        return plain.values() if clean else plain

    def all_methods(self, clean=True):
        plain = OrderedDict() if self.parent is None else self.parent.all_methods(False)
        for method in self.methods:
            plain[method.name] = (method, self)
        return plain.values() if clean else plain

    def conforms_to(self, other):
        return other.bypass() or self == other or self.parent is not None and self.parent.conforms_to(other)

    def bypass(self):
        return False
    
    def can_be_inherited(self):
        return True

    def __str__(self):
        output = f'type {self.name}'
        parent = '' if self.parent is None else f' : {self.parent.name}'
        output += parent
        output += ' {'
        output += '\n\t' if self.attributes or self.methods else ''
        output += '\n\t'.join(str(x) for x in self.attributes)
        output += '\n\t' if self.attributes else ''
        output += '\n\t'.join(str(x) for x in self.methods)
        output += '\n' if self.methods else ''
        output += '}\n'
        return output

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.conforms_to(other) and other.conforms_to(self)

class ErrorType(Type):
    def __init__(self):
        Type.__init__(self, '<error>')

    def conforms_to(self, other):
        return True

    def bypass(self):
        return True

    def __eq__(self, other):
        return isinstance(other, Type)


class ObjectType(Type):
    def __init__(self):
        Type.__init__(self, 'Object')

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, ObjectType)    

class IOType(Type):
    def __init__(self):
        Type.__init__(self, 'IO')

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, IOType)

class StringType(Type):
    def __init__(self):
        Type.__init__(self, 'String')

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, StringType)

    def can_be_inherited(self):
        return False

class BoolType(Type):
    def __init__(self):
        Type.__init__(self, 'Bool')

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, BoolType)

    def can_be_inherited(self):
        return False

class IntType(Type):
    def __init__(self):
        Type.__init__(self, 'Int')

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, IntType)
    
    def can_be_inherited(self):
        return False

class SelfType(Type):
    def __init__(self):
        Type.__init__(self, 'SELF_TYPE')
    
    def can_be_inherited(self):
        return False

class AutoType(Type):
    def __init__(self):
        Type.__init__(self, 'AUTO_TYPE')

    def can_be_inherited(self):
        return False

    def conforms_to(self, other):
        return True

    def bypass(self):
        return True
    

class Context:
    def __init__(self):
        self.types = {}

    def create_type(self, name:str):
        if name in self.types:
            raise SemanticError(f'Type with the same name ({name}) already in context.')
        typex = self.types[name] = Type(name)
        return typex

    def get_type(self, name:str):
        try:
            return self.types[name]
        except KeyError:
            raise SemanticError(f'Type "{name}" is not defined.')

    def __str__(self):
        return '{\n\t' + '\n\t'.join(y for x in self.types.values() for y in str(x).split('\n')) + '\n}'

    def __repr__(self):
        return str(self)

class VariableInfo:
    def __init__(self, name, vtype, idx):
        self.name = name
        self.type = vtype
        self.idx = idx

class Scope:
    def __init__(self, parent=None):
        self.locals = []
        self.parent = parent
        self.children = []
        self.index = 0 if parent is None else len(parent)

    def __len__(self):
        return len(self.locals)

    def create_child(self):
        child = Scope(self)
        self.children.append(child)
        return child

    def define_variable(self, vname, vtype, idx=None):
        info = VariableInfo(vname, vtype, idx)
        self.locals.append(info)
        return info

    def find_variable(self, vname, index=None):
        locals = self.locals if index is None else itt.islice(self.locals, index)
        try:
            return next(x for x in locals if x.name == vname)
        except StopIteration:
            return self.parent.find_variable(vname, self.index) if self.parent is None else None

    def is_defined(self, vname):
        return self.find_variable(vname) is not None

    def is_local(self, vname):
        return any(True for x in self.locals if x.name == vname)


class InferencerManager:
    def __init__(self, context):
        # given a type represented by int idx, types[idx] = (A, B), where A and B are sets
        # if x in A then idx.conforms_to(x)
        # if x in B then x.conforms_to(idx)
        self.conforms_to = []
        self.conformed_by = []
        self.count = 0
        self.context = context

        self.obj = 'object'


    def assign_id(self):
        idx = self.count
        self.conforms_to.append({self.obj})
        self.conformed_by.append(set())
        self.count += 1

        return idx

    def upd_conforms_to(self, idx, other):
        sz = len(self.conforms_to[idx])
        self.conforms_to[idx].update(other)

        return sz != len(self.conforms_to[idx])

    def upd_conformed_by(self, idx, other):
        sz = len(self.conformed_by[idx])
        self.conformed_by[idx].update(other)

        return sz != len(self.conformed_by[idx])

    def auto_to_type(self, idx, typex):
        sz = len(self.conforms_to[idx])
        self.conforms_to[idx].add(typex.name)

        return sz != len(self.conforms_to[idx])

    def type_to_auto(self, idx, typex):
        sz = len(self.conformed_by[idx])
        self.conformed_by[idx].add(typex.name)

        return sz != len(self.conformed_by[idx])
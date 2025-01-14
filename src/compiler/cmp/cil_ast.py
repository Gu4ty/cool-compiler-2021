class Node:
    pass


class ProgramNode(Node):
    def __init__(self, dottypes, dotdata, dotcode):
        self.dottypes = dottypes
        self.dotdata = dotdata
        self.dotcode = dotcode


class TypeNode(Node):
    def __init__(self, name):
        self.name = name
        self.attributes = []
        self.methods = []


class DataNode(Node):
    def __init__(self, vname, value):
        self.name = vname
        self.value = value


class FunctionNode(Node):
    def __init__(self, fname, params, localvars, instructions):
        self.name = fname
        self.params = params
        self.localvars = localvars
        self.instructions = instructions
        self.ids = dict()
        self.labels_count = 0


class ParamNode(Node):
    def __init__(self, name):
        self.name = name


class LocalNode(Node):
    def __init__(self, name):
        self.name = name


class InstructionNode(Node):
    pass


class AssignNode(InstructionNode):
    def __init__(self, dest, source):
        self.dest = dest
        self.source = source


class ArithmeticNode(InstructionNode):
    def __init__(self, dest, left, right):
        self.dest = dest
        self.left = left
        self.right = right


class PlusNode(ArithmeticNode):
    pass


class MinusNode(ArithmeticNode):
    pass


class StarNode(ArithmeticNode):
    pass


class DivNode(ArithmeticNode):
    pass


class LeqNode(ArithmeticNode):
    pass


class LessNode(ArithmeticNode):
    pass


class EqualNode(ArithmeticNode):
    pass


class EqualStrNode(EqualNode):
    pass


class GetAttribNode(InstructionNode):
    def __init__(self, dest, obj, attr, computed_type):
        self.dest = dest
        self.obj = obj
        self.attr = attr
        self.computed_type = computed_type


class SetAttribNode(InstructionNode):
    def __init__(self, obj, attr, value, computed_type):
        self.obj = obj
        self.attr = attr
        self.value = value
        self.computed_type = computed_type


class GetIndexNode(InstructionNode):
    pass


class SetIndexNode(InstructionNode):
    pass


class AllocateNode(InstructionNode):
    def __init__(self, itype, dest):
        self.type = itype
        self.dest = dest


class ArrayNode(InstructionNode):
    pass


class TypeOfNode(InstructionNode):
    def __init__(self, obj, dest):
        self.obj = obj
        self.dest = dest


class LabelNode(InstructionNode):
    def __init__(self, label):
        self.label = label


class GotoNode(InstructionNode):
    def __init__(self, label):
        self.label = label


class GotoIfNode(InstructionNode):
    def __init__(self, condition, label):
        self.condition = condition
        self.label = label


class StaticCallNode(InstructionNode):
    def __init__(self, function, dest):
        self.function = function
        self.dest = dest


class DynamicCallNode(InstructionNode):
    def __init__(self, xtype, method, dest, computed_type):
        self.type = xtype
        self.method = method
        self.dest = dest
        self.computed_type = computed_type


class ArgNode(InstructionNode):
    def __init__(self, name):
        self.name = name


class ReturnNode(InstructionNode):
    def __init__(self, value=None):
        self.value = value


class LoadNode(InstructionNode):
    def __init__(self, dest, msg):
        self.dest = dest
        self.msg = msg


class ExitNode(InstructionNode):
    pass


class TypeNameNode(InstructionNode):
    def __init__(self, dest, source):
        self.dest = dest
        self.source = source


class NameNode(InstructionNode):
    def __init__(self, dest, name):
        self.dest = dest
        self.name = name


class CopyNode(InstructionNode):
    def __init__(self, dest, source):
        self.dest = dest
        self.source = source


class LengthNode(InstructionNode):
    def __init__(self, dest, source):
        self.dest = dest
        self.source = source


class ConcatNode(InstructionNode):
    def __init__(self, dest, prefix, suffix, length):
        self.dest = dest
        self.prefix = prefix
        self.suffix = suffix
        self.length = length


class SubstringNode(InstructionNode):
    def __init__(self, dest, str_value, index, length):
        self.dest = dest
        self.str_value = str_value
        self.index = index
        self.length = length


class ReadStrNode(InstructionNode):
    def __init__(self, dest):
        self.dest = dest


class ReadIntNode(InstructionNode):
    def __init__(self, dest):
        self.dest = dest


class PrintStrNode(InstructionNode):
    def __init__(self, value):
        self.value = value


class PrintIntNode(InstructionNode):
    def __init__(self, value):
        self.value = value


class ComplementNode(InstructionNode):
    def __init__(self, dest, obj):
        self.dest = dest
        self.obj = obj


class VoidNode(InstructionNode):
    pass


class ErrorNode(InstructionNode):
    def __init__(self, data_node):
        self.data_node = data_node

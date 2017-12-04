
indent = ""


# token class for ASTs
class Token:
    def __init__(self, type, value, ndx):
        self.type = type
        self.value = value
        self.ndx = ndx

    def pretty(self):
        return "\n" + indent + "Token('%s', '%s')\n" % (self.type, self.value)

    def to_str(self):
        return "Token('%s', '%s')" % (self.type, self.value)


# default AST node class
class ASTNode:
    def __init__(self, name):
        self.name = name
        self.content = []

    def pretty(self):
        global indent
        indent += " "
        pretty_string = "\n" + indent + self.name + ":[\n"
        indent += " "
        for item in self.content:
            pretty_string += item.pretty()
        indent = indent[:len(indent) - 2]
        return pretty_string + "\n" + indent + " ]\n"

    def to_str(self):
        str_string = self.name + ":["
        for item in self.content:
            str_string += item.to_str()
        return str_string + "]"


# holder class for final AST
class AST:
    def __init__(self, content):
        self.content = [content]

    def to_str(self):
        string = ""
        for item in self.content:
            string += item.pretty()
        return string


# removes unnecessary nodes from AST
def reduce(ast):
    content = ast.content
    if len(content) == 1:
        if isinstance(content[0], Token):
            return ast
        else:
            return reduce(content[0])
    else:
        for num in range(len(content)):
            item = content[num]
            if isinstance(item, ASTNode):
                content[num] = reduce(item)
        return ast


# convert parse tree to AST
def get_ast(parse_tree):
    ast = reduce(AST(parse_tree))
    return ast

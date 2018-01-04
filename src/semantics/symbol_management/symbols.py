import src.semantics.symbol_management.variables as variables
from src.parser.ASTtools import ASTNode
from src.semantics.semantics import SemanticConstruct
from src.semantics.import_func import import_package

declarations = {
    "variable_declaration": variables.var_parse,
    "struct_block": variables.struct_parse,
    "interface_block": variables.struct_parse,
    "type_block": variables.struct_parse,
    "func_block": variables.func_parse,
    "macro_block": variables.macro_parse,
    "async_block": variables.func_parse,
    "constructor_block": variables.func_parse
}


# builds the symbol table
def construct_symbol_table(ast, scope=0):
    symbol_table = []
    for item in ast.content:
        if isinstance(item, ASTNode):
            if item.name == "block":
                symbol_table.append(construct_symbol_table(item, scope + 1))
            elif item.name in declarations:
                variables.s_table = symbol_table
                if item.name in ["func_block", "variable_declaration", "async_block"]:
                    if item.name in ["func_block", "async_block"]:
                        func = variables.func_parse(item, scope)
                        for sub_tree in item.content:
                            if sub_tree.name == "functional_block":
                                func.code = SemanticConstruct(construct_symbol_table(sub_tree.content[1]), sub_tree.content[1])
                        symbol_table.append(func)
                    else:
                        symbol_table.append(declarations[item.name](item, scope))
                else:
                    if item.name == "macro_block":
                        macro = variables.macro_parse(item)
                        for sub_tree in item.content:
                            if sub_tree.name == "functional_block":
                                macro.code = SemanticConstruct(construct_symbol_table(sub_tree.content[1]), sub_tree.content[1])
                        symbol_table.append(macro)
                    else:
                        symbol_table.append(declarations[item.name](item))
            elif item.name == "module_block":
                mod = variables.module_parse(item)
                for sub_tree in item.content:
                    if isinstance(sub_tree, ASTNode):
                        if sub_tree.name == "module_main":
                            mod.constructor = variables.module_constructor_parse(sub_tree.content[0])
                            for component in sub_tree.content[0].content:
                                if isinstance(component, ASTNode):
                                    if component.name == "constructional_block":
                                        if isinstance(component.content[0], ASTNode):
                                            mod.constructor.code = SemanticConstruct(construct_symbol_table(component.content[0]), component.content[0])
                            if len(sub_tree.content) > 1:
                                mod.members = sub_tree.content[1]
                symbol_table.append(mod)
            elif item.name == "import_stmt":
                # TODO get package name
                symbol_table.append(import_package("", True, ""))
            else:
                construct_symbol_table(item, scope)
    return symbol_table

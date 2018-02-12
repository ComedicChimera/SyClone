from src.semantics.symbols.symbol_table import construct_symbol_table
from src.parser.ASTtools import ASTNode
from src.errormodule import throw
from src.semantics.checker.semantic_checker import check
from src.semantics.semantics import SemanticConstruct


# checks to see if contextual statements were placed correctly
def check_context(ast, loop, func):
    for item in ast.content:
        if isinstance(item, ASTNode):
            # update if in loop
            if item.name in ["for_block", "do_block", "lambda_stmt"]:
                check_context(item, True, func)
            # update if in function
            elif item.name == "functional_block":
                check_context(item, loop, True)
            # catch returns not placed in functional region
            elif item.name == "return_stmt" and not func:
                throw("semantic_error", "Unable to return from region", item)
            # catches loop returns not placed in a functional region
            elif item.name in ["break_stmt", "continue_stmt"] and not loop:
                throw("semantic_error", "Invalid loop jump", item)
            # descend
            else:
                check_context(item, loop, func)


# the main semantic checker function
def check_ast(ast):
    # construct main symbol table
    table = construct_symbol_table(ast)
    # check for basic contextual statements
    check_context(ast, False, False)
    # run main check function on ast
    check(ast, table)
    # return object containing table and ast
    return SemanticConstruct(table, ast)

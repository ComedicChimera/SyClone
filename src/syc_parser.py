import src.gramtools as gramtools
import src.errormodule as er
import src.ASTtools as ASTtools


class Parser:
    def __init__(self):
        self.follow_table = {}

    def parse(self, tokens):
        # gets grammar for gramtools
        g = gramtools.build_grammar()
        # gets a set of follows to be used later
        # self.get_follows(g)
        # generates parsing table
        # p_table = self.generate_table(g, self.follow_table)
        # calls main parsing algorithm
        node = self.run_parser(g.productions, g, tokens)
        print(node)
        return node

    def run_parser(self, table, grammar, input_buffer):
        # the stack is going to hold the main parsing content
        stack = ["$", grammar.start_symbol]
        # this is going to hold the ASTs in construction
        semantic_stack = []
        # the position in the input buffer
        pos = 0
        # enter the main parsing cycle
        while len(stack) > 0:
            # holds the current symbol on the stack
            symbol = stack[-1]
            # if the symbol is a terminal, compare to input buffer
            if isinstance(symbol, tuple):
                if symbol[1] in grammar.terminals:
                    # if they are equal, add Token obj to current AST in semantic stack and pop both
                    if symbol == input_buffer[pos]:
                        semantic_stack[-1].content.append(ASTtools.Token(input_buffer[pos][1], input_buffer[pos][0]))
                        pos += 1
                        stack.pop()
                    else:
                        er.throw("syntax error", "Unexpected Token", [pos, input_buffer])
            # if the symbol is $, break
            elif symbol == "$":
                break
            # if symbol is epsilon, pop and continue
            elif symbol == "&":
                stack.pop()
            # handles closing of ASTS
            elif symbol == "queue":
                semantic_stack[-2].content.append(semantic_stack[-1])
                semantic_stack.pop()
            # if symbol is non terminal, add the predict set to the stack and create new AST node
            elif symbol in grammar.nonterminals or symbol == grammar.start_symbol:
                semantic_stack.append(ASTtools.ASTNode(symbol))
                stack.pop()
                stack.append(table[symbol])
            else:
                # renames symbol for sake of clarity
                predict_set = self.get_predict_set(symbol, grammar)
                # if current input symbol is a possibility accept it, shift productions and add accepted terminal to stack + next predict set
                if input_buffer[pos][1] in predict_set or "&" in predict_set:
                    stack.pop()
                    predict_stack = self.eliminate_bad_predict_sets(input_buffer[pos][1], symbol, grammar)
                    predict_stack = self.predict_expand(predict_stack, grammar)
                    predict_sets = []
                    for predict_item in predict_stack:
                        if predict_item not in predict_sets:
                            predict_sets.append(predict_item)
                    predict_stack = predict_sets
                    if all(x[0] in grammar.terminals for x in predict_stack):
                        trim_stack = [x[1:] for x in predict_stack if len(x[1:]) > 0]
                        if len(trim_stack) > 0:
                            stack.append(trim_stack)
                        stack.append(input_buffer[pos])
                    else:
                        stack.append(predict_stack)
                else:
                    er.throw("syntax error", "Unexpected Token", [pos, input_buffer])

        # return the first item in the semantic stack (the main AST)
        return semantic_stack[0]

    @staticmethod
    def predict_expand(predict_stack, grammar):
        new_predict_stack = []
        for predict_set in predict_stack:
            if predict_set[0] in grammar.nonterminals:
                productions = grammar.productions[predict_set[0]]
                new_predict_stack += productions + predict_set
            else:
                new_predict_stack.append(predict_set)
        return new_predict_stack

    def get_predict_set(self, predict_stack, grammar):
        predict_set = []
        for item in predict_stack:
            if item[0] in grammar.nonterminals:
                predict_set += self.first(grammar, grammar.productions[item[0]])
            else:
                predict_set.append(item[0])
        return predict_set

    def eliminate_bad_predict_sets(self, terminal, predict_sets, grammar):
        new_p_sets = []
        for p_set in predict_sets:
            if p_set[0] == terminal:
                new_p_sets.append(p_set)
            elif p_set[0] in grammar.nonterminals:
                if terminal in self.first(grammar, grammar.productions[p_set[0]]):
                    new_p_sets.append(p_set)
        return new_p_sets

    def first(self, grammar, production):
        # primes first list
        first_list = []

        # sets up add to first list function to make processing easier
        def add_to_first_list(obj):
            if isinstance(obj, list):
                for item in obj:
                    if item not in first_list:
                        first_list.append(item)
            else:
                if obj not in first_list:
                    first_list.append(obj)
        # iterates through sub-pros
        position = 0
        for item in production:
            # if first item is a terminal, add to first list
            if item[position] in grammar.terminals:
                add_to_first_list(item[position])
            elif item[position] == "&":
                add_to_first_list(item[position])
                position += 1
                add_to_first_list(self.epsilon_firsts(grammar, item, position))
            # if first item in non-terminal, recur and add the result to first list
            else:
                first = self.first(grammar, grammar.productions[item[position]])
                if "&" in first:
                    add_to_first_list(self.epsilon_firsts(grammar, item, position + 1))
                add_to_first_list(first)
        return first_list

    def epsilon_firsts(self, grammar, production, position):
        if position + 1 > len(production) - 1:
            return []
        elif production[position] in grammar.nonterminals:
            return self.first(grammar, grammar.productions[production[position]])
        elif production[position] == "&":
            return self.epsilon_firsts(grammar, production, position + 1)
        else:
            return production[position]

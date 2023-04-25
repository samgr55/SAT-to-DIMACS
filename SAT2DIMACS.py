from sympy.core.symbol import Symbol
from sympy.logic.boolalg import to_cnf, And, Or, Not
from sympy.abc import A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z
from os import path
import os,sys
import subprocess
import glob



class DimacsMapping:
    def __init__(self):
        self._symbol_to_variable = {}
        self._variable_to_symbol = {}
        self._total_variables = 0

    @property
    def total_variables(self):
        return self._total_variables

    def new_variable(self):
        self._total_variables += 1
        return self._total_variables

    def get_variable_for(self, symbol):
        result = self._symbol_to_variable.get(symbol)
        if result is None:
            result = self.new_variable()
            self._symbol_to_variable[symbol] = result
            self._variable_to_symbol[result] = symbol

        return result

    def get_symbol_for(self, variable):
        return self._variable_to_symbol[variable]

    def __str__(self) -> str:
        return str(self._variable_to_symbol)

class DimacsFormula:
    def __init__(self, mapping, clauses):
        self._mapping = mapping
        self._clauses = clauses

    @property
    def mapping(self):
        return self._mapping

    @property
    def clauses(self):
        return self._clauses

    def __str__(self):
        header = f"p cnf {self._mapping.total_variables} {len(self._clauses)}"
        body = "\n".join(
            " ".join([str(literal) for literal in clause] + ["0"])
            for clause in self._clauses
        )

        return "\n".join([header, body])

def to_dimacs_formula(sympy_cnf):
    dimacs_mapping = DimacsMapping()
    dimacs_clauses = []

    assert type(sympy_cnf) == And
    for sympy_clause in sympy_cnf.args:
        assert type(sympy_clause) == Or

        dimacs_clause = []
        for sympy_literal in sympy_clause.args:
            if type(sympy_literal) == Not:
                sympy_symbol, polarity = sympy_literal.args[0], -1
            elif type(sympy_literal) == Symbol:
                sympy_symbol, polarity = sympy_literal, 1
            else:
                raise AssertionError("invalid cnf")

            dimacs_variable = dimacs_mapping.get_variable_for(sympy_symbol)
            dimacs_literal = dimacs_variable * polarity
            dimacs_clause.append(dimacs_literal)

        dimacs_clauses.append(dimacs_clause)

    return DimacsFormula(dimacs_mapping, dimacs_clauses)

def to_dimacs_tseitin(sympy_formula):
    dimacs_mapping = DimacsMapping()
    dimacs_clauses = []

    formula_literal = _to_dimacs_tseitin_literal(
        sympy_formula, dimacs_mapping, dimacs_clauses
    )
    dimacs_clauses.append([formula_literal])

    return DimacsFormula(dimacs_mapping, dimacs_clauses)

def _to_dimacs_tseitin_literal(sympy_formula, dimacs_mapping, dimacs_clauses):

    if type(sympy_formula) == Symbol:
        return dimacs_mapping.get_variable_for(sympy_formula)

    args_literals = [
        _to_dimacs_tseitin_literal(arg, dimacs_mapping, dimacs_clauses)
        for arg in sympy_formula.args
    ]


    if type(sympy_formula) == Not:
        return -args_literals[0]

    result = dimacs_mapping.new_variable()

    if type(sympy_formula) == And:
        for arg_literal in args_literals:
            dimacs_clauses.append([-result, arg_literal])
        dimacs_clauses.append(
            [result] + [-arg_literal for arg_literal in args_literals]
        )
    elif type(sympy_formula) == Or:
        for arg_literal in args_literals:
            dimacs_clauses.append([result, -arg_literal])
        dimacs_clauses.append(
            [-result] + [arg_literal for arg_literal in args_literals]
        )
    else:
        
        raise NotImplementedError()

    return result


f= to_cnf(~(A&~Z |~(H|D|K&~A)) | ((C|D&A&H|(K&B|~L&W))) | (K & ~F | (B&P&~Q) | (~P|~A|C)) & (L&U|~B) | (N&B&~A) | (L|H&~S |(C&F&~S|(H|~D&F))))

print(f)


f_dimacs = to_dimacs_tseitin(f)


print(f_dimacs)




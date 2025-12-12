#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projet TL : parser - requires Python version >= 3.10
"""

import sys
from math import factorial

assert sys.version_info >= (3, 10), "Use Python 3.10 or newer !"

import lexer
from definitions import V_T, str_attr_token

#####
# Variables internes (à ne pas utiliser directement)

_current_token = V_T.END
_value = None  # attribut du token renvoyé par le lexer


#####
# Fonctions génériques

class ParserError(Exception):
    pass


def unexpected_token(expected):
    return ParserError("Found token '" + str_attr_token(_current_token, _value) + "' but expected " + expected)


def get_current():
    return _current_token


def init_parser(stream):
    global _current_token, _value
    lexer.reinit(stream)
    _current_token, _value = lexer.next_token()
    # print("@ init parser on",  repr(str_attr_token(_current, _value)))  # for DEBUGGING


def consume_token(tok):
    # Vérifie que le prochain token est tok ;
    # si oui, le consomme et renvoie son attribut ; si non, lève une exception
    global _current_token, _value
    if _current_token != tok:
        raise unexpected_token(tok.name)
    if _current_token != V_T.END:
        old = _value
        _current_token, _value = lexer.next_token()
        return old

def recover(suiv):
    curr = get_current()
    while curr not in suiv and curr != V_T.END and curr != V_T.SEQ:
        consume_token(curr)
        curr = get_current()

#########################
## Parsing de input et exp

results = []

def parse_input():
    global results
    results = []
    tok = get_current()
    if tok == V_T.END:
        return results
    while True:
        # Consommer tous les séparateurs SEQ consécutifs
        while get_current() == V_T.SEQ:
            consume_token(V_T.SEQ)
            continue
        if get_current() == V_T.END:
            break
        val = parse_exp5()
        results.append(val)
        recover({V_T.SEQ})
        
    return results


def parse_exp5():
    cumul = parse_exp4()
    n = parse_exp5_prime(cumul)
    return n

def parse_exp5_prime(cumul):
    tok = get_current()
    if tok == V_T.ADD:
        consume_token(tok)
        # Vérifier si on peut parser une expression
        if get_current() in (V_T.END, V_T.SEQ):
            return cumul  # Ignorer l'opérateur si l'opérande manque
        n2 = parse_exp4()
        return parse_exp5_prime(cumul + n2)
    elif tok == V_T.SUB:
        consume_token(tok)
        # Vérifier si on peut parser une expression
        if get_current() in (V_T.END, V_T.SEQ):
            return cumul  # Ignorer l'opérateur si l'opérande manque
        n2 = parse_exp4()
        return parse_exp5_prime(cumul - n2)
    else:
        return cumul


def parse_exp4():
    cumul = parse_exp3()
    n = parse_exp4_prime(cumul)
    return n


def parse_exp4_prime(cumul):
    tok = get_current()
    if tok == V_T.MUL:
        consume_token(tok)
        #On verifie si on peut parser une expression (pour éviter la division par zéro)
        if get_current() in (V_T.END, V_T.SEQ):
            return cumul  # Ignorer l'opérateur si l'opérande manque
        n2 = parse_exp3()
        return parse_exp4_prime(cumul * n2)
    elif tok == V_T.DIV:
        consume_token(tok)
        # On verifie si on peut parser une expression (pour éviter la division par zéro)
        if get_current() in (V_T.END, V_T.SEQ):
            return cumul  #On ignore l'opérateur si le nombre suivant est manquant
        n2 = parse_exp3()
        return parse_exp4_prime(cumul / n2)
    else:
        return cumul


def parse_exp3():
    tok = get_current()
    if tok == V_T.SUB:
        consume_token(tok)
        n = parse_exp3()
        return -n
    elif tok in (V_T.NUM, V_T.CALC, V_T.OPAR):
        return parse_exp2()
    else:
        recover((V_T.SUB,V_T.NUM, V_T.CALC,V_T.OPAR))
        #Note pour souvenir : si après récupération on est à END ou SEQ, on ne peut plus parser une expression
        if get_current() in (V_T.END, V_T.SEQ):
            return 0 
        return parse_exp3()


def parse_exp2():
    cumul = parse_exp1()
    n = parse_exp2_prime(cumul)
    return n


def parse_exp2_prime(cumul):
    tok = get_current()
    if tok == V_T.FACT:
        consume_token(tok)
        return parse_exp2_prime(factorial(cumul))
    else:
        return cumul


def parse_exp1():
    base = parse_exp0()
    return parse_exp1_prime(base)


def parse_exp1_prime(base):
    if get_current() == V_T.POW:
        consume_token(V_T.POW)
        exp = parse_exp1()
        return pow(base, exp)
    return base


def parse_exp0():
    tok = get_current()
    if tok == V_T.NUM:
        val = consume_token(tok)
        return val
    if tok == V_T.CALC:
        idx = consume_token(V_T.CALC)
        if idx <= 0 or idx > len(results):
            raise ValueError(f"Invalid calcul reference #{idx}")
        return results[idx - 1]
    elif tok == V_T.OPAR:
        consume_token(tok)
        val = parse_exp5()
        while get_current() == V_T.CPAR:
            consume_token(get_current())
        return val
    else:
        recover((V_T.NUM, V_T.CALC, V_T.OPAR))
        if get_current() == V_T.END:
            return 0 #Ou raise parseError

        return parse_exp0()


#####################################
## Fonction principale de la calculatrice
## Appelle l'analyseur grammatical et retourne
## - None sans les attributs
## - la liste des valeurs des calculs avec les attributs

def parse(stream=sys.stdin):
    init_parser(stream)
    l = parse_input()
    consume_token(V_T.END)
    return l


#####################################
## Test depuis la ligne de commande

if __name__ == "__main__":
    print("@ Testing the calculator in infix syntax.")
    result = parse()
    if result is None:
        print("@ Input OK ")
    else:
        print("@ result = ", repr(result))

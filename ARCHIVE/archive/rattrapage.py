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

#########################
## Parsing de input et exp

def recover(suiv):
    
    while get_current() not in suiv and get_current() != V_T.END:
        consume_token(get_current())
    
    if get_current() == V_T.END:
        raise ParserError("Parsing error: unexpected end of input.")
    
    
    return get_current()

def parse_input(L=[]):
    match get_current():
        case V_T.END:
            return L
        case V_T.NUM | V_T.CALC | V_T.OPAR | V_T.SUB:
            n = parse_exp5(L)
            consume_token(V_T.SEQ)
            L = L + [n]
            L = parse_input(L)

            return L
        case _:
            recover([V_T.NUM, V_T.CALC, V_T.OPAR, V_T.SUB,V_T.END])
            parse_input(L)

def parse_exp5(L):
    match get_current():
        case V_T.NUM | V_T.CALC | V_T.OPAR | V_T.SUB:
            n_1 = parse_exp4(L)
            n = parse_Z(L,n_1)
            return n
        case _:
            recover([V_T.NUM, V_T.CALC, V_T.OPAR, V_T.SUB])
            parse_exp5(L)

def parse_Z(L,n_1):
    match get_current():
        case V_T.ADD | V_T.SUB:
            n_2 = parse_exp5_bis(L,n_1)
            n_3 = parse_Z(L,n_2)
            return n_3
        case V_T.CPAR | V_T.SEQ:
            return n_1
        case _:
            recover([V_T.ADD, V_T.SUB, V_T.CPAR, V_T.SEQ])
            parse_Z(L,n_1)

def parse_exp5_bis(L,n_1):
    match get_current():
        case V_T.ADD:
            consume_token(V_T.ADD)
            n_2 = parse_exp4(L)
            return n_1 + n_2
        case V_T.SUB:
            consume_token(V_T.SUB)
            n_2 = parse_exp4(L)
            return n_1 - n_2
        case _:
            recover([V_T.ADD, V_T.SUB])
            parse_exp5_bis(L,n_1)

def parse_exp4(L):
    match get_current():
        case V_T.NUM | V_T.CALC | V_T.OPAR | V_T.SUB:
            n_1 = parse_exp3(L)
            n = parse_Y(L,n_1)
            return n
        case _:
            recover([V_T.NUM, V_T.CALC, V_T.OPAR, V_T.SUB])
            parse_exp4(L)

def parse_Y(L,n_1):
    match get_current():
        case V_T.MUL | V_T.DIV:
            n_2 = parse_exp4_bis(L,n_1)
            n_3 = parse_Y(L,n_2)
            return n_3
        case V_T.CPAR | V_T.ADD | V_T.SUB | V_T.SEQ:
            n_3 = n_1
            return n_3
        case _:
            recover([V_T.MUL, V_T.DIV, V_T.CPAR, V_T.ADD, V_T.SUB, V_T.SEQ])
            parse_Y(L,n_1)

def parse_exp4_bis(L,n_1):
    match get_current():
        case V_T.MUL:
            consume_token(V_T.MUL)
            n_2 = parse_exp3(L)
            n = n_1 * n_2
            return n
        case V_T.DIV:
            consume_token(V_T.DIV)
            n_2 = parse_exp3(L)
            return n_1 / n_2
        case _:
            recover([V_T.MUL, V_T.DIV])
            parse_exp4_bis(L,n_1)

def parse_exp3(L):   
    match get_current():
        case V_T.SUB:
            consume_token(V_T.SUB)
            n_1 = parse_exp3(L)
            n = -1 * n_1
            return n
        case V_T.NUM | V_T.CALC | V_T.OPAR:
            n = parse_exp2(L)
            return n 
        case _:
            recover([V_T.SUB, V_T.NUM, V_T.CALC, V_T.OPAR])
            parse_exp3(L)

def parse_exp2(L):
    match get_current():
        case V_T.NUM | V_T.CALC | V_T.OPAR:
            n_1 = parse_exp1(L)
            n = parse_exp2_bis(n_1)
            return n
        case _:
            recover([V_T.NUM, V_T.CALC, V_T.OPAR])
            parse_exp2(L)

def parse_exp2_bis(n):
    match get_current():
        case V_T.FACT:
            consume_token(V_T.FACT)
            return factorial(int(n))
        case V_T.CPAR | V_T.MUL | V_T.DIV | V_T.ADD | V_T.SUB | V_T.SEQ:
            return n
        case _:
            recover([V_T.FACT, V_T.CPAR, V_T.MUL, V_T.DIV, V_T.ADD, V_T.SUB, V_T.SEQ])
            parse_exp2_bis(n)

def parse_exp1(L):
    match get_current():
        case V_T.NUM | V_T.CALC | V_T.OPAR:
            n_1 = parse_exp0(L)
            n = parse_exp1_bis(L,n_1)
            return n
        case _:
            recover([V_T.NUM, V_T.CALC, V_T.OPAR])
            parse_exp1(L)

def parse_exp1_bis(L,n):
    match get_current():
        case V_T.POW:
            consume_token(V_T.POW)
            n_1 = parse_exp1(L)
            return n**n_1
        case V_T.CPAR | V_T.FACT | V_T.MUL | V_T.DIV | V_T.ADD | V_T.SUB | V_T.SEQ:
            return n
        case _:
            recover([V_T.POW, V_T.CPAR, V_T.FACT, V_T.MUL, V_T.DIV, V_T.ADD, V_T.SUB, V_T.SEQ])
            parse_exp1_bis(L,n)

def parse_exp0(L):
    match get_current():
        case V_T.NUM:
            n = consume_token(V_T.NUM)
            return n
        case V_T.CALC:
            i = consume_token(V_T.CALC)
            print(i)
            n = L[i-1]
            return n
        case V_T.OPAR:
            consume_token(V_T.OPAR)
            n = parse_exp5(L)
            consume_token(V_T.CPAR)
            return n
        case _:
            recover([V_T.NUM, V_T.CALC, V_T.OPAR])
            parse_exp0(L)




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


#########
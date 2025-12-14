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
#Ici, on implémente chacune des fonctions parse en fonction de notre Grammaire LL(1) qu'on a obtenu avec les directeurs#
#Voici ci dessous la grammaire qu'on a obtenu : 
"""
Grammaire LL(1) implémentée :

Input    -> Exp5 SEQ Input
          | epsilon

Exp5     -> Exp4 Z
Z        -> Exp5Bis Z
          | epsilon
Exp5Bis  -> ADD Exp4
          | SUB Exp4

Exp4     -> Exp3 Y
Y        -> Exp4Bis Y
          | epsilon
Exp4Bis  -> MUL Exp3
          | DIV Exp3

Exp3     -> SUB Exp3
          | Exp2

Exp2     -> Exp1 Exp2Bis
Exp2Bis  -> FACT
          | epsilon

Exp1     -> Exp0 Exp1Bis
Exp1Bis  -> POW Exp1
          | epsilon

Exp0     -> NUM
          | CALC
          | OPAR Exp5 CPAR
"""
def parse_input():
    
    match get_current():
        case V_T.END:
            return
        case V_T.NUM | V_T.CALC | V_T.OPAR | V_T.SUB:
            parse_exp5()
            consume_token(V_T.SEQ)
            parse_input()
            return
        case _:
            raise unexpected_token("NUM, CALC, OPAR, SUB, END")

def parse_exp5():
    match get_current():
        case V_T.NUM | V_T.CALC | V_T.OPAR | V_T.SUB:
            parse_exp4()
            parse_Z()
            return
        case _:
            raise unexpected_token("NUM, CALC, OPAR, SUB")

def parse_Z():
    match get_current():
        case V_T.ADD | V_T.SUB:
            parse_exp5_bis()
            parse_Z()
            return
        case V_T.CPAR | V_T.SEQ:
            return
        case _:
            raise unexpected_token("NADD, SUB, CPAR, SEQ")

def parse_exp5_bis():
    match get_current():
        case V_T.ADD:
            consume_token(V_T.ADD)
            parse_exp4()
            return
        case V_T.SUB:
            consume_token(V_T.SUB)
            parse_exp4()
            return
        case _:
            raise unexpected_token("ADD, SUB")

def parse_exp4():
    match get_current():
        case V_T.NUM | V_T.CALC | V_T.OPAR | V_T.SUB:
            parse_exp3()
            parse_Y()
            return
        case _:
            raise unexpected_token("NUM, CALC, OPAR, SUB")

def parse_Y():
    match get_current():
        case V_T.MUL | V_T.DIV:
            parse_exp4_bis()
            parse_Y()
            return
        case V_T.CPAR | V_T.ADD | V_T.SUB | V_T.SEQ:
            return
        case _:
            raise unexpected_token("MUL, DIV, CPAR, ADD, SUB, SEQ")

def parse_exp4_bis():
    match get_current():
        case V_T.MUL:
            consume_token(V_T.MUL)
            parse_exp3()
            return
        case V_T.DIV:
            consume_token(V_T.DIV)
            parse_exp3()
            return
        case _:
            raise unexpected_token("MUL, DIV")

def parse_exp3():   
    match get_current():
        case V_T.SUB:
            consume_token(V_T.SUB)
            parse_exp3()
            return
        case V_T.NUM | V_T.CALC | V_T.OPAR:
            parse_exp2()
            return
        case _:
            raise unexpected_token("SUB, NUM, CALC, OPAR")

def parse_exp2():
    match get_current():
        case V_T.NUM | V_T.CALC | V_T.OPAR:
            parse_exp1()
            parse_exp2_bis()
            return
        case _:
            raise unexpected_token("NUM, CALC, OPAR")

def parse_exp2_bis():
    match get_current():
        case V_T.FACT:
            consume_token(V_T.FACT)
            return
        case V_T.CPAR | V_T.MUL | V_T.DIV | V_T.ADD | V_T.SUB | V_T.SEQ:
            return
        case _:
            raise unexpected_token("FACT, CPAR, MUL, DIV, ADD, SUB, SEQ")

def parse_exp1():
    match get_current():
        case V_T.NUM | V_T.CALC | V_T.OPAR:
            parse_exp0()
            parse_exp1_bis()
            return
        case _:
            raise unexpected_token("NUM, CALC, OPAR")

def parse_exp1_bis():
    match get_current():
        case V_T.POW:
            consume_token(V_T.POW)
            parse_exp1()
            return
        case V_T.CPAR | V_T.FACT | V_T.MUL | V_T.DIV | V_T.ADD | V_T.SUB | V_T.SEQ:
            return 
        case _:
            raise unexpected_token("POW, CPAR, FACT, MUL, DIV, ADD, SUB, SEQ")

def parse_exp0():
    match get_current():
        case V_T.NUM:
            consume_token(V_T.NUM)
            return
        case V_T.CALC:
            consume_token(V_T.CALC)
            return
        case V_T.OPAR:
            consume_token(V_T.OPAR)
            parse_exp5()
            consume_token(V_T.CPAR)
            return
        case _:
            raise unexpected_token("NUM, CALC, OPAR")



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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projet TL : lexer de la calculatrice
"""

import sys
import enum
import definitions as defs


# Pour lever une erreur, utiliser: raise LexerError("message décrivant l'erreur dans le lexer")
class LexerError(Exception):
    pass


#################################
# Variables et fonctions internes (privées)

# Variables privées : les trois prochains caractères de l'entrée
current_char1 = ''
current_char2 = ''
current_char3 = ''

# Initialisation: on vérifie que EOI n'est pas dans V_C et on initialise les prochains caractères
def init_char():
    global current_char1, current_char2, current_char3
    # Vérification de cohérence: EOI n'est pas dans V_C ni dans SEP
    if defs.EOI in defs.V_C:
        raise LexerError('character ' + repr(defs.EOI) + ' in V_C')
    defs.SEP = {' ', '\n', '\t'} - set(defs.EOI)
    defs.V = set(tuple(defs.V_C) + (defs.EOI,) + tuple(defs.SEP))
    current_char1 = defs.INPUT_STREAM.read(1)
    # print("@", repr(current_char1))  # decomment this line may help debugging
    if current_char1 not in defs.V:
        raise LexerError('Character ' + repr(current_char1) + ' unsupported')
    if current_char1 == defs.EOI:
        current_char2 = defs.EOI
        current_char3 = defs.EOI
    else:
        current_char2 = defs.INPUT_STREAM.read(1)
        # print("@", repr(current_char2))  # decomment this line may help debugging
        if current_char2 not in defs.V:
            raise LexerError('Character ' + repr(current_char2) + ' unsupported')
        if current_char2 == defs.EOI:
            current_char3 = defs.EOI
        else:
            current_char3 = defs.INPUT_STREAM.read(1)
            # print("@", repr(current_char3))  # decomment this line may help debugging
            if current_char3 not in defs.V:
                raise LexerError('Character ' + repr(current_char3) + ' unsupported')

    return

# Accès aux caractères de prévision
def peek_char3():
    global current_char1, current_char2, current_char3
    return (current_char1 + current_char2 + current_char3)

def peek_char1():
    global current_char1
    return current_char1

# Avancée d'un caractère dans l'entrée
def consume_char():
    global current_char1, current_char2, current_char3
    if current_char2 == defs.EOI: # pour ne pas lire au delà du dernier caractère
        current_char1 = defs.EOI
        return
    if current_char3 == defs.EOI: # pour ne pas lire au delà du dernier caractère
        current_char1 = current_char2
        current_char2 = defs.EOI
        return
    next_char = defs.INPUT_STREAM.read(1)
    # print("@", repr(next_char))  # decommenting this line may help debugging
    if next_char in defs.V:
        current_char1 = current_char2
        current_char2 = current_char3
        current_char3 = next_char
        return
    raise LexerError('Character ' + repr(next_char) + ' unsupported')

def expected_digit_error(char):
    return LexerError('Expected a digit, but found ' + repr(char))

def unknown_token_error(char):
    return LexerError('Unknown start of token ' + repr(char))

# Initialisation de l'entrée
def reinit(stream=sys.stdin):
    global input_stream, current_char1, current_char2, current_char3
    assert stream.readable()
    defs.INPUT_STREAM = stream
    current_char1 = ''
    current_char2 = ''
    current_char3 = ''
    init_char()


#################################
## Automates pour les entiers et les flottants


def read_INT_to_EOI():

    etats = ["q0","q1","puit"]
    etat_finaux = ["q1"]
    etat_init = "q0"
    etat = etat_init


    while peek_char1() not in defs.EOI:
        match etat:
            case "q0":
                match peek_char1():

                    case "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9":
                        etat = "q1"
                    case _:
                        etat = "puit"

            case "q1":
                match peek_char1():
                
                    case "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9":
                        etat = "q1"
                    case _:
                        etat = "puit"

            case "puit": 
                etat = "puit"

        consume_char()

    return (etat in etat_finaux)


def read_FLOAT_to_EOI():

    etats = ["q0","q1","q2","q3","puit"]
    etat_finaux = ["q3"]
    etat_init = "q0"
    etat = etat_init


    while peek_char1() not in defs.EOI:
        match etat:
            case "q0":
                match peek_char1():

                    case "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9":
                        etat = "q2"
                    case ".":
                        etat = "q1"
                    case _:
                        etat = "puit"

            case "q1":
                match peek_char1():

                    case "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9":
                        etat = "q3"
                    case _:
                        etat = "puit"

            case "q2":
                match peek_char1():

                    case "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9":
                        etat = "q2"
                    case ".":
                        etat = "q3"
                    case _ :
                        etat = "puit"

            case "q3":
                match peek_char1():

                    case "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9":
                        etat = "q3"
                    case _ :
                        etat = "puit"

            case "puit": 
                etat = "puit"

        consume_char()
    
    return (etat in etat_finaux) 


#################################
## Lecture de l'entrée: entiers, nombres, tokens

#Lecture d'un chiffre, puis avancée et renvoi de sa valeur
def read_digit():
    current_char = peek_char1()
    if current_char not in defs.DIGITS:
        raise expected_digit_error(current_char)
    value = eval(current_char)
    consume_char()
    return value


# Lecture d'un entier en renvoyant sa valeur
def read_INT():
    "Fonction lisant un entier et renvoyant sa valeur"
    current_char = peek_char1()
    if current_char not in defs.DIGITS:
        raise expected_digit_error(current_char1)

    value = 0
    # On continue jusqu'à ce qu'on trouve un EOI
    while current_char in defs.DIGITS:
        digit = read_digit()   # lit + consomme un chiffre
        value = value * 10 + digit 
        current_char = peek_char1()
    return value

global int_value
global exp_value
global sign_value

# Lecture d'un nombre en renvoyant sa valeur
def read_NUM():

    etats = ["q0","q1","q2","q3","q4","q5","q6","puit"]
    etat_finaux = ["q2","q3","q6"]
    etat_init = "q0"
    etat = etat_init

    max = "" #Pour stocker le lexème  de taille maximal reconnu pour l'instant

    mantisse = 0.0
    exposant_signe = None
    exposant_valeur = 0.0

    div = 0.1  #Pour la partie après la virgule, on divisera par 10 à chaque chiffre lu

    while peek_char1() not in defs.EOI and etat != "puit": #etat != "puit" pour s'arrêter dès qu'on est dans le puit et ne pas consomer + que le max sinon on "mange" les prochains lexèmes, problématique pour la fonction next_token

        match etat:
            case "q0":
                match peek_char1():

                    case "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9":
                        etat = "q3"
                        mantisse = mantisse * 10 + float(peek_char1()) #On ajoute la valeur du nouveau chiffre en "décalant" la mantisse sur la gauche (*10)
                    case ".":
                        etat = "q1"
                    case _:
                        etat = "puit"

            case "q1":
                match peek_char1():

                    case "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9":
                        etat = "q2"
                        mantisse = mantisse + float(peek_char1())*div
                        div = div/10 #On divise par 10 pour le prochain chiffre après la virgule
                    case _:
                        etat = "puit"

            case "q2":
                match peek_char1():

                    case "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9":
                        etat = "q2"
                        mantisse = mantisse + float(peek_char1())*div
                        div = div/10
                    case "E"|"e":
                        etat = "q4"
                        exposant_signe = "+" 
                    case _:
                        etat = "puit"

            case "q3":
                match peek_char1():

                    case "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9":
                        etat = "q3"
                        mantisse = mantisse * 10 + float(peek_char1())
                    case ".":
                        etat = "q2"
                    case "E"|"e":
                        etat = "q4"
                        exposant_signe = "+" 
                    case _:
                        etat = "puit"
            
            case "q4":
                match peek_char1():

                    case "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9":
                        etat = "q6"
                        exposant_valeur = exposant_valeur*10 + float(peek_char1())
                    case "+":
                        etat = "q5"
                        exposant_signe = "+"
                    case "-":
                        etat = "q5"
                        exposant_signe = "-"
                    case _:
                        etat = "puit"

            case "q5":
                match peek_char1():

                    case "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9":
                        etat = "q6"
                        exposant_valeur = exposant_valeur*10 + float(peek_char1())
                    case _:
                        etat = "puit"

            case "q6":
                match peek_char1():

                    case "0"|"1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9":
                        etat = "q6"
                        exposant_valeur = exposant_valeur*10 + float(peek_char1())
                    case _:
                        etat = "puit"

            case "puit": 
                etat = "puit"

        if etat != "puit":
            consume_char()
        
        if (etat in etat_finaux):
            max = max + peek_char1()

    if exposant_signe == "+":
        exposant_signe = 1
    if exposant_signe == "-":
        exposant_signe = -1
    if exposant_signe == None:
        exposant_signe = 0

    return (mantisse) * (10**(exposant_signe*exposant_valeur))


# Parse un lexème (sans séparateurs) de l'entrée et renvoie son token.
# Cela consomme tous les caractères du lexème lu.
def read_token_after_separators():

    char1 = peek_char1()
    if char1 in defs.EOI:
        consume_char()
        return (defs.V_T.END,None)
    if char1 in ['+', '-', '*', '/', '^', '!', '(', ')', ';']:
        consume_char()
        return (defs.TOKEN_MAP[char1],None)

    if char1 == "#":
        consume_char()
        return (defs.V_T.CALC,read_INT())
        
    return (defs.V_T.NUM,read_NUM())

# Donne le prochain token de l'entrée, en sautant les séparateurs éventuels en tête
# et en consommant les caractères du lexème reconnu.
def next_token():

    while peek_char1() in defs.SEP:
        consume_char()

    return read_token_after_separators()


#################################
## Fonctions de tests

def test_INT_to_EOI():
    print("@ Testing read_INT_to_EOI. Type a word to recognize.")
    reinit()
    if read_INT_to_EOI():
        print("Recognized")
    else:
        print("Not recognized")

def test_FLOAT_to_EOI():
    print("@ Testing read_FLOAT_to_EOI. Type a word to recognize.")
    reinit()
    if read_FLOAT_to_EOI():
        print("Recognized")
    else:
        print("Not recognized")

def test_lexer():
    print("@ Testing the lexer. Just type tokens and separators on one line")
    reinit()
    token, value = next_token()
    while token != defs.V_T.END:
        print("@", defs.str_attr_token(token, value))
        token, value = next_token()

if __name__ == "__main__":
    ## Choisir une seule ligne à décommenter
    ##test_INT_to_EOI()
    #test_FLOAT_to_EOI()
    test_lexer()

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


    while peek_char1() != defs.EOI:
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


    while peek_char1() != defs.EOI:
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


# Lecture d'un chiffre, puis avancée et renvoi de sa valeur
def read_digit():
    current_char = peek_char1()
    if current_char not in defs.DIGITS:
        raise expected_digit_error(current_char)
    value = eval(current_char)
    consume_char()
    return value


# Lecture d'un entier en renvoyant sa valeur
# Lecture d'un entier en renvoyant sa valeur
def read_INT():
    current_char = peek_char1()
    if current_char not in defs.DIGITS:
        raise expected_digit_error(current_char1)

    value = 0
    # On cntinue jusqu'à ce qu'on trouve un EOI
    while current_char in defs.DIGITS:
        digit = read_digit()   # lit + consomme un chiffre
        value = value * 10 + digit 
        current_char = peek_char1()
    return value

#Qq petites remarques pour toi : je te mens pas le value = value*10+ digit c'est chatgpt il m'a proposé ça et en vrai c'est assez malin pck 
#Imaginons on lit le mot 234243 
#Au début on lit 2 après on va chercher à avoir 23 et 23 = 2*10 +3 donc 3 correspond au read_digit
#et la value c'est celle qu'on a itéré 
#Sinon le code en lui même c'est comme celui de read_digit() avec une boucle

global int_value
global exp_value
global sign_value

# Lecture d'un nombre en renvoyant sa valeur

#Pour cette fonction, voici ce que je comprends elle doit lire un nombre et si on se réferre à l'automate c'est des integers 
#En gros la partie avant la virgule ; après il y a la virgule (c'est le dot dans la façon que le prof a défini)
#Puis on a l'exposant et après on a encore des digits 
#Alors le problème c'est que dans l'automate on rentre à q0 ok, on finit à q6,q2,q3 ok mais je ne comprends pas cmt on peut lui dire
#de s'arreter à q2 ou q3 ?
#Si t'as une idée je suis preneur 
#PS : je pense on peut faire comme ce que t'as fais avec read_FLOAT_to_EOI
# PRoblème je vois pas le "." dans l'automate donc je vais faire comme si on doit un lire en partant 
# de leur définiton : number = (integer ∪ pointfloat) (exponent ∪ {ε}


def read_NUM():    
    mantisse = 0
    current_char = peek_char1()
    #Ici, la mantisse on lit jusqu'à la virgule la virgule étant représenté par le point
    #Partie entière
    while current_char in defs.DIGITS:
        digit = read_digit()
        mantisse = mantisse*10 + digit
        current_char = peek_char1()

    #REMARQUE : ICI, on peut simplement mantisse = read_INT() 
    #comme ça on lit direct la partie entière

    if current_char == "." : #Pour la virgule 
        consume_char()
        current_char = peek_char1()
        if current_char not in defs.DIGITS:
            raise expected_digit_error(current_char) #Après la virgule il doit y avoir des chiffres
        div = 0.1
        while current_char in defs.DIGITS:
            digit = read_digit()
            mantisse += digit * div
            div /= 10
            current_char = peek_char1()

        #Maintenant, on passe à l'exposant
    valeur_exposant = 0
    signe_exposant = 1  
    #1 pour dire que c'est positif -1 pour exprimer les inverses
    #Partie Exposant
    if current_char == "e" or current_char == "E":
        consume_char()
        current_char = peek_char1()
        if current_char  not in ("+" , "-") and current_char not in defs.DIGITS: #Après la puissance il faut un plus ou un chiffre
            raise expected_digit_error(current_char)
            #Alors là l'erreur j'ai fais comme read_digit() 
            #tout en haut du fichier lexer.py ils disent d'utiliser Lexer pour lever l'erreur
            #Tu veux qu'on laisse comme ça ou pas ?
        if current_char == "+" : 
           consume_char() 
           current_char = peek_char1()
           #ici le signe_exposant est 1 pas besoin de le repréciser
        if current_char == "-" : #pck arpès le E il y a forcément soit un + soit un - 
            consume_char()
            signe_exposant = -1 
            current_char = peek_char1()
        while current_char in defs.DIGITS :  #je pense current_char != defs.EOI ca doit marcher là pck techniquement après la virgule tous les digits ce sera la fin
            digit = read_digit()
            valeur_exposant = valeur_exposant*10 + digit
            current_char = peek_char1()

    apres_virgule = 10**(signe_exposant*valeur_exposant)
    return mantisse*apres_virgule
        
#Alors ca marche j'ai utilisé chatGPT Pour qq petits trucs et comprendre la structure (je pense pas que ca te dérange)
#j'ai globalement tout compris le seul truc un peu flou c'est pour la partie de la virgule le div j'ai un gros doute je pense qu'on peut s'en passer
#J'avais fais une version sans 


# Parse un lexème (sans séparateurs) de l'entrée et renvoie son token.
# Cela consomme tous les caractères du lexème lu.
def read_token_after_separators():
    print("@ATTENTION: lexer.read_token_after_separators à finir !") # LIGNE A SUPPRIMER
    return (defs.V_T.END, None) # par défaut, on renvoie la fin de l'entrée


# Donne le prochain token de l'entrée, en sautant les séparateurs éventuels en tête
# et en consommant les caractères du lexème reconnu.
def next_token():
    print("@ATTENTION: lexer.next_token à finir !") # LIGNE A SUPPRIMER
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

def test_read_NUM(): #FONCTION PUREMENT CHATGPT pour essayer la méthode read_NUM()
    print("@ Testing read_NUM. Type a number (integer, float, or with exponent).")
    reinit()  # réinitialise le flux d'entrée
    try:
        value = read_NUM()
        print("read_NUM() returned:", value)
    except LexerError as e:
        print("LexerError:", e)

if __name__ == "__main__":
    ## Choisir une seule ligne à décommenter
    ##test_INT_to_EOI()
    test_read_NUM()
    #test_FLOAT_to_EOI()
    #read_INT()
    #test_lexer()

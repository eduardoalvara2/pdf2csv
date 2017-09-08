#!/usr/bin/env python
# -*- coding: utf-8 -*-
#######################################################
# Created by: Gabo Flowers <https://github.com/gaboflowers>
# Source: https://github.com/gaboflowers/servel-padron 
#         luxuryParser.py
#######################################################
import re

regex_manyEspacios = re.compile("\s[\s]+")

def nameparser(nombre):
    palabras = nombre.split()
    if len(palabras) == 2:
        return (nombre,palabras[1],palabras[0],"")
    nombre = nombre.strip(' ')
    i_esp = nombre.find(' ')
    ap1 = nombre[:i_esp]
    i_esp2 = nombre.find(' ',i_esp+1)
    ap2 = nombre[i_esp+1:i_esp2]
    n_pila = nombre[max(i_esp2+1,i_esp):]

    Foreign_Starts = set(["J","K","C","P","T","X","F","Z","Y","G","H","Q"])
    def tipo_del(s):
        return (len(s) <= 3 and not any([s.startswith(c) for c in Foreign_Starts]) and\
                not s in ["RIO","MAR","SOL","REY"]) or s in ["SAN","SANTO","SANTA","SANT"]

    #apellidos frasales
    try:
        if len(ap1) <= 3 or len(ap2) <= 3:
            l_nombre = nombre.split()
            len_ap_1 = 1
            if tipo_del(l_nombre[0]):
                if not tipo_del(l_nombre[1]):
                    ap1 = " ".join([l_nombre[0],l_nombre[1]])
                    len_ap_1 +=1
                else:
                    ap1 = " ".join([l_nombre[0],l_nombre[1],l_nombre[2]])
                    len_ap_1 +=2
            else:
                ap_1 = l_nombre[0]

            i_ap_m = len_ap_1
            i_f = i_ap_m
            if tipo_del(l_nombre[i_ap_m]):
                if not tipo_del(l_nombre[i_ap_m+1]):
                    ap2 = " ".join([l_nombre[i_ap_m],l_nombre[i_ap_m+1]])
                    i_f = i_ap_m+1
                else:
                    ap2 = " ".join([l_nombre[i_ap_m],l_nombre[i_ap_m+1],l_nombre[i_ap_m+2]])
                    i_f = i_ap_m+2
            else:
                ap2 = l_nombre[i_ap_m]
            n_pila = " ".join(l_nombre[i_f+1:])
        if n_pila == "":
            n_pila = ap2
            ap2 = ""
        elif n_pila.startswith("DE "):
            #"CASTRO SOLIS DE OVANDO PAULINA ANDREA DE LA SANTISIMA TRINIDAD;15471103", independencia
            l_nombre = n_pila.split()
            ap2 += " " + l_nombre[0] + " " + l_nombre[1]
            n_pila = " ".join(l_nombre[2:])
    except IndexError:
        pass
    
    nombre = re.sub(regex_manyEspacios," ",nombre)
    return (ap1, ap2, n_pila, nombre)

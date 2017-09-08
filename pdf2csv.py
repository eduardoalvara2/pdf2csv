#!/usr/bin/env python
# -*- coding: utf-8 -*-
#######################################################
# Created by: Eduardo Alvarado <eduardoalvara2@gmail.com>
#######################################################
# *** THIS SCRIPT USE 'pdfToText' of 'poppler-0.51' TO WORK ***

import os
import sys
import traceback
import codecs
import time
from subprocess import call
from loggerconf import log
from nameparser import nameparser

debug = False #False for production
pwd = os.getcwd
cd  = lambda x: os.chdir(x)
ls  = lambda : os.listdir(pwd())
archsHere  = None
lastLine = 0
numpdf = 0
ti   = 0

def txt2csv(filename):

    #Procesamos el archivo
    global debug
    global ti
    global lastLine
    current = {'region':'','provincia':'','comuna':'','pagina':''}

    def isNotValid(line):
    #Validate if the date 
        pos=0
        if( line[:70].find("PADRON ELECTORAL") > 0 ):
            return True
        if( line[:18]=="SERVICIO ELECTORAL" ):
            #Get the Comuna
            posRegion = line.find('REGI')
            posComuna = line.find('COMUNA')
            posPagina = line.find('GINA')-3
            current['region'] = line[posRegion+line[posRegion:posComuna].find(":")+1:posComuna].strip()
            current['comuna'] = line[posComuna+line[posComuna:posPagina].find(":")+1:posPagina].strip()
            current['pagina'] = line[posPagina:].strip()
            return True
        if( line[:70].find('PROVINCIA') > 0 ):
            posProvincia = line.find(':')
            current['provincia'] = line[posProvincia+1:].strip()
            return True
        return False
    
    #Initialize vars for "for"
    circunsPos = 0
    separator  = ";"
    iFailed = {'empty':0,'onlyname':0,'abrutend':0} #fails counter
    csvLine = ""
    rutPos  = 0
    csvn = os.path.join('csvs',filename+'.csv')
    txt  = codecs.open(os.path.join('txts',filename+'.txt'),'rU','utf-8')
    csv  = open(csvn,'w')
    t = 0 # records counter
    i = 0 # only records added counter

    if debug:
        print >> csv, "sep="+separator

    for line in txt:

        #initialize the line
        line = line.encode('utf-8')
        lineLen = len(line)

        #Here is saved the line to the csv (It begins after the first loop)
        if csvLine:
            if rutPos>lineLen>1:
                nombreContinuation = line.strip()
                nombreRaw+=" "+nombreContinuation 
                log.info(nombreContinuation+" was concatenate at end of the column nombreRaw in record with rut "+csvLine[1:8].replace(separator,'')+".")
            #Nombre is parser to get "apellido_paterno,apellido_materno,nombre,nombre_completo"
            nombreTuple  = nameparser(nombreRaw)
            csvLineTuple = (nombreTuple[0],nombreTuple[1],nombreTuple[2],nombreRaw,csvLine)
            csvLine = separator.join(csvLineTuple)
            print >> csv, csvLine
            if not nombreTuple[1]:
                log.error('Record had not apellido_materno. Added anyways. '+csvLine)
            i+=1
        csvLine = ""

        #Validate if is a record
        if(isNotValid(line)):
            continue
        if(line[:6]=='NOMBRE'):
            rutPos = line.find('C.IDENTIDAD')
            circunsPos = line.find('CIRCUNSCRIPCI')
            continue

        #if is a record, count it
        t+=1

        #GET NOMBRE
        nombreRaw = line[:rutPos].strip()
        if not nombreRaw:
            iFailed['empty']+=1
            continue
        #IMPORTANT: The name will be added when the next loop starts

        #GET RUT
        generoPos=rutPos+16
        rawRut = line[rutPos:generoPos].strip()
        if not rawRut:
            log.warning(nombreRaw+" near the record "+str(i)+" only had a floating Nombre. Record ignored")
            iFailed['onlyname']+=1
            csvLine = ""
            continue
        rutArr = rawRut.replace('.','').split('-',1)
        rut = rutArr[0]
        csvLine += rut
        csvLine += separator

        #GET DV
        dv = rutArr[1]
        csvLine += dv
        csvLine += separator

        #GET GENERO
        domicilioPos=generoPos+4
        genero = line[generoPos:domicilioPos].strip()
        csvLine += genero
        csvLine += separator

        #GET DOMICILIO
        domicilio = line[domicilioPos:circunsPos].strip()
        j=0
        #If the address is in diferent lines
        while(lineLen<circunsPos):
            j+=1
            line = txt.readline().encode('utf-8')
            lineLen = len(line)
            if(isNotValid(line)): 
                log.warning(nombreRaw+" with rut "+rut+" near the record "+str(i)+" had an abrut end reading his Domicilio. Record ignored")
                iFailed['abrutend']+=1
                csvLine = ""
                break
            domicilio += " "+line[domicilioPos:circunsPos].strip()
            if(j>=7):
                break
        if(isNotValid(line)): 
            csvLine = ""
            continue
        csvLine += domicilio
        csvLine += separator

        #GET CIRCUNSCRIPCION
        csvLine += current['region']
        csvLine += separator
        csvLine += current['provincia']
        csvLine += separator
        csvLine += current['comuna']
        csvLine += separator

        #GET MESA
        mesaPos = lineLen-6
        mesa = line[mesaPos:].strip()
        csvLine += mesa
        csvLine += separator

        #Source File
        fuente = filename+".pdf "+current['pagina']
        csvLine += fuente
        #endfor

    txt.close()
    csv.close()
    ti+=i

    #report
    log.info(str(i)+" of "+str(t)+" records written SUCCESSFULLY to "+csvn+".")
    if(iFailed['empty']>0):
        log.warning(str(iFailed['empty'])+" failed because they were empty.")
    if(iFailed['onlyname']>0):
        log.warning(str(iFailed['onlyname'])+" failed because they only had a floating Nombre.")
    if(iFailed['abrutend']>0):
        log.warning(str(iFailed['abrutend'])+" failed because they had an abrut end.")

if __name__ == '__main__':

    globalStartTime = time.clock()
    archsHere = ls()
    filefound =False
    
    #We create the files dirs
    directories=['csvs','txts','used_pdfs']
    for directory in directories :
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    log.info("Start")

    #PDFS TO TXTS
    log.info("Processing pdfs")
    for f in archsHere:
        if f.endswith(".pdf"):
            filefound = True
            numpdf+=1
            startTime = time.clock()

            filename = f[:f.find(".pdf")] #name(from 0 to '.pdf' position)
            pdfn = filename+".pdf"
            txtn = filename+".txt"

            log.info(pdfn+"...")

            #Using 'pdfToText' of 'poppler-0.51', we convert the pdf to text
            call(["pdftotext", "-layout", pdfn, txtn])

            usedpdfn = os.path.join('used_pdfs',pdfn)
            if not debug:
                #move pdf to used_pdf folder
                if os.path.exists(usedpdfn):
                    os.remove(usedpdfn)
                os.rename(pdfn,usedpdfn)

            #Show time lapse
            timeLapse = str(round(time.clock()-startTime,2))
            log.info(pdfn+" done in "+timeLapse+"s.")

    archsHere = ls()
    if not filefound:
        log.warning("No pdfs found in root folder.")
    filefound =False

    #TXTS TO CSVS
    log.info("Processing txts")
    for f in archsHere:
        if f.endswith(".txt"):
            filefound = True
            startTime = time.clock()

            filename = f[:f.find(".txt")] #name(from 0 to '.txt' position)
            txtn = filename+".txt"
            newTxt = os.path.join('txts',txtn)

            log.info(txtn+"...")

            
            #We move the .txt to 'txts' folder
            if os.path.exists(newTxt):
                os.remove(newTxt)
            os.rename(txtn,newTxt)

            #Convert  text to csv
            txt2csv(filename)

            #Show time lapse
            timeLapse = str(round(time.clock()-startTime,2))
            log.info(txtn+" done in "+timeLapse+"s.")

    if not filefound:
        log.warning("No txts found in root folder.")

    timeLapse = str(round(time.clock()-globalStartTime,2))
    log.info("End. "+str(ti)+" records from "+str(numpdf)+" pdfs written to their corresponding csv files")
    log.info("TIME OF EXECUTION: "+timeLapse+"s.")
    log.info(".")



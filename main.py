#!/usr/bin/python3

import sys
import arrow
import json
from ics import Calendar, Event

giorni_settimana = ['lun', 'mar', 'mer', 'gio', 'ven', 'sab', 'dom']

# def break_orari(orari_lines: list) -> list:
    # """Prima parte del parsing, spezza i blocchi ritornando lista di liste
    # dei singoli blocchi (associati ad una persona)"""
    # size = len(orari_lines) + 1
    # idx_list = [idx + 1 for idx, val in
                # enumerate(orari_lines) if val == '\n']
    # persone = [orari_lines[i: j-1] for i, j in
               # zip([0] + idx_list, 
                   # idx_list + ([size] if idx_list[-1] != size else []))] 
    # return persone
# 
# def get_orari(persone: list) -> set:
    # """Dalla lista dei blocchi ricava la mappa: persona : lista degli
    # orari relativi ai giorni in cui è di turno"""
    # orari = {}
    # for persona in persone:
        # nome_persona = persona[0].replace('\n','').replace(':', '')
        # orari.setdefault(nome_persona, {})
        # for entry in persona[1:]:
            # giorno_lavorativo = entry.split(': ')
            # giorno = giorno_lavorativo[0].replace(':','').replace('\t','')
            # for turno in giorno_lavorativo[1].split(' '):
                # list_turno = [ora.replace('\n', '') for ora in turno.split('-')]
                # print(list_turno)
                # if giorno in orari[nome_persona]:
                    # orari[nome_persona][giorno].append(list_turno)
                # else:
                    # orari[nome_persona].setdefault(giorno,[])
                    # orari[nome_persona][giorno].append(list_turno)
    # return orari

def load_orari(orari_file: str) -> set:
    """carica il file `orari_file' ritornando la mappa {persona: [lista
    dei turni giorno per giorno]}"""
    # orari_raw = break_orari(open(orari_file).readlines())
    # orari = get_orari(orari_raw)
    with open(orari_file, 'r') as json_file:
        orari = json.load(json_file)
    return orari

def presenti(orari_di_lavoro: set, giorno: str) -> list:
    """Dagli orari di lavoro e il giorno indicato ritorna la lista di
    persone presenti"""
    presenti_giorno = []
    for persona in orari_di_lavoro:
        if giorno in orari_di_lavoro[persona]:
           presenti_giorno.append([persona, orari_di_lavoro[persona][giorno]])
    return presenti_giorno

def check_disponibilita(presenti_giorno: set, ora: arrow.Arrow, lista_persone: list) -> set:
    """Dalle persone di turno, l'ora indicata e la lista di tutte le
    persone ricava una mappa della disponibilità delle persone: chiave:
    nome persona, valore: booleano che indica se la persona è di turno o
    meno"""
    disponibilita = {}
    for persona in presenti_giorno:
        nome_persona = persona[0]
        orari_persona = persona[1]
        for turno in orari_persona:
            inizio_turno = arrow.get(ora.format('YYYY-MM-DDT') + turno['start'])
            fine_turno = arrow.get(ora.format('YYYY-MM-DDT') + turno['end'])
            if ora >= inizio_turno and ora < fine_turno:
                disponibilita[nome_persona] = turno['details']
            elif nome_persona not in disponibilita:
                disponibilita[nome_persona] = 'non disponibile'
    return disponibilita

# def disponibili(disponibilita: set) -> list:
    # """Dal set che indica la disponibilità (chiave: nome persona, valore:
    # booleano che indica se è disponibile o meno), ricava una lista di
    # persone al momento disponibili"""
    # disponibili = []
    # for persona in disponibilita:
        # if disponibilita[persona]:
            # disponibili.append(persona)
    # return disponibili

def persone_di_turno(orari_di_lavoro: set, ora: arrow.Arrow) -> list:
    """Dal set con gli orari din lavoro e l'ora indicata ricava la lista
    delle persone di turno"""
    giorno = giorni_settimana[int(ora.format('d')) - 1]
    presenti_giorno = presenti(orari_di_lavoro, giorno)
    disponibilita = check_disponibilita(presenti_giorno, ora, [persona for persona in orari_di_lavoro])
    return disponibilita

def get_impegni(cal: Calendar) -> set:
    """Dal calendario `cal' tira fuori un set elle persone impegnate coi
    loro impegni: chiave: persona impegnata, valore: lista di eventi che
    la impegnano (eventi del tipo Event, importato da ics)"""
    impegni = {}
    for impegno in cal.events:
        nome_persona = impegno.name.replace(' ', '')
        if nome_persona in impegni:
            impegni[nome_persona].append(impegno)
        else:
            impegni[nome_persona] = [impegno]
    return impegni

def get_impegnati(impegni: set, ora: arrow.Arrow) -> set:
    """Dagli impegni e l'ora specificata tira fuori un set degli
    impegnati: chiave: nome della persona impegnata, valore: la
    descrizione dell'impegno"""
    impegnati = {}
    for persona in impegni:
        for impegno in impegni[persona]:
            if impegno.begin <= ora and impegno.end > ora:
                impegnati[persona] = impegno.description
    return impegnati

def main(file_orario, file_impegni, ora: str = arrow.now().format('YYYY-MM-DD HH:mm')):
    
    ora = arrow.get(ora)
    impegni = get_impegni(Calendar(open(file_impegni).read()))
    orari_di_lavoro = load_orari(file_orario)
    di_turno = persone_di_turno(orari_di_lavoro, ora)
    print(di_turno)
    # impegnati = get_impegnati(impegni, ora)

    # disponibilita = {persona: 'Non in servizio' for persona in orari_di_lavoro}
 
    # for persona in di_turno:
        # disponibilita[persona] = 'in servizio'
 
    # for persona in impegnati:
        # disponibilita[persona] = impegnati[persona]

    # print(disponibilita)
            
if __name__ == "__main__":
    if(len(sys.argv) < 3):
        print("help: [nome_script] file_orari.or file_impegni.ics [timestamp +%FT%H:%M]")
    else:
        if(len(sys.argv) < 4):
            main(sys.argv[1], sys.argv[2])
        else:
            main(sys.argv[1], sys.argv[2], sys.argv[3])

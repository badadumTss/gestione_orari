#!/usr/bin/python3

import sys
import arrow
from ics import Calendar, Event
from orari import *

giorni_settimana = ['lun', 'mar', 'mer', 'gio', 'ven', 'sab', 'dom']

def break_orari(orari_lines: list):
    size = len(orari_lines) + 1
    idx_list = [idx + 1 for idx, val in
                enumerate(orari_lines) if val == '\n']
    persone = [orari_lines[i: j-1] for i, j in
               zip([0] + idx_list, 
                   idx_list + ([size] if idx_list[-1] != size else []))] 
    return persone

def get_orari(persone: list) -> set:
    orari = {}
    for persona in persone:
        nome_persona = persona[0].replace('\n','').replace(':', '')
        orari.setdefault(nome_persona, {})
        for entry in persona[1:]:
            giorno_lavorativo = entry.split(': ')
            giorno = giorno_lavorativo[0].replace(':','').replace('\t','')
            for turno in giorno_lavorativo[1].split(' '):
                list_turno = [ora.replace('\n', '') for ora in turno.split('-')]
                if giorno in orari[nome_persona]:
                    orari[nome_persona][giorno].append(list_turno)
                else:
                    orari[nome_persona].setdefault(giorno,[])
                    orari[nome_persona][giorno].append(list_turno)
    return orari

def load_orari(orari_file: str) -> set:
    orari_raw = break_orari(open(orari_file).readlines())
    orari = get_orari(orari_raw)
    return orari

def presenti(orari_di_lavoro: set, giorno: str) -> list:
    presenti_giorno = []
    for persona in orari_di_lavoro:
        if giorno in orari_di_lavoro[persona]:
           presenti_giorno.append([persona, orari_di_lavoro[persona][giorno]])
    return presenti_giorno

def check_disponibilita(presenti_giorno: set, ora: arrow.Arrow, lista_persone: list) -> set:
    disponibilita = {persona: False for persona in lista_persone}
    for persona in presenti_giorno:
        nome_persona = persona[0].replace(':', '')
        orari_persona = persona[1]
        for turno in orari_persona:
            if len(turno) > 1:
                inizio_turno = arrow.get(ora.format('YYYY-MM-DDT') + turno[0])
                fine_turno = arrow.get(ora.format('YYYY-MM-DDT') + turno[1])
                if ora >= inizio_turno and ora < fine_turno:
                    disponibilita[nome_persona] = True
    return disponibilita

def disponibili(disponibilita: set) -> list:
    disponibili = []
    for persona in disponibilita:
        if disponibilita[persona]:
            disponibili.append(persona)
    return disponibili

def persone_di_turno(orari_di_lavoro: set, ora: arrow.Arrow) -> list:
    giorno = giorni_settimana[int(ora.format('d')) - 1]
    presenti_giorno = presenti(orari_di_lavoro, giorno)
    disponibilita = check_disponibilita(presenti_giorno, ora, [persona for persona in orari_di_lavoro])
    return disponibili(disponibilita)

def get_impegni(cal: Calendar) -> set:
    impegni = {}
    for impegno in cal.events:
        if impegno.name in impegni:
            impegni[impegno.name].append(impegno)
        else:
            impegni[impegno.name] = [impegno]
    return impegni

def get_impegnati(impegni: set, ora: arrow.Arrow) -> set:
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
    impegnati = get_impegnati(impegni, ora)
                
    disponibilita = {persona: 'Non in servizio' for persona in orari_di_lavoro}

    for persona in di_turno:
        disponibilita[persona] = 'in servizio'

    for persona in impegnati:
        disponibilita[persona] = impegnati[persona]
    
    print(disponibilita)
            
if __name__ == "__main__":
    if(len(sys.argv) < 3):
        print("help: [nome_script] file_orari.or file_impegni.ics [timestamp +%FT%H:%M]")
    else:
        if(len(sys.argv) < 4):
            main(sys.argv[1], sys.argv[2])
        else:
            main(sys.argv[1], sys.argv[2], sys.argv[3])

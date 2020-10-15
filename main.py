#!/bin/env python3
import sys
import arrow
from ics import Calendar, Event
from orari import *

def main(file_orario, file_impegni, ora = arrow.now()):
    cal_impegni = Calendar(open(file_impegni).read())
    
    impegni = {}
    for impegno in cal_impegni.events:
        if impegno.name in impegni:
            impegni[impegno.name].append(impegno)
        else:
            impegni[impegno.name] = [impegno]
    
    # orari_di_lavoro mappa generata in orari.py, interpretata da orari.or
    orari_di_lavoro = load_orari(file_orario)
    di_turno = interseca(orari_di_lavoro, ora)

    impegnati = []
    for persona in impegni:
        for impegno in impegni[persona]:
            if impegno.begin <= ora and impegno.end > ora:
                impegnati.append(persona.replace(' ', ''))

    disponibilita = {}
    for persona in di_turno:
        if persona in impegnati:
            disponibilita[persona] = False
        else:
            disponibilita[persona] = True
    
    # DEBUG
    # print(impegni)
    # print(impegnati)
    print(disponibilita)
            
if __name__ == "__main__":
    if(len(sys.argv) < 3):
        print("""help: [nome_script] file_orari.or file_impegni.ics [timestamp "+%Y-%m-%dT%H:%m"]""")
    else:
        if(len(sys.argv) < 4):
            main(sys.argv[1], sys.argv[2])
        else:
            main(sys.argv[1], sys.argv[2], sys.argv[3])

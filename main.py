#!/usr/bin/python3

import sys
import arrow
from ics import Calendar, Event
from orari import *

def main(file_orario, file_impegni, ora: str = arrow.now().format('YYYY-MM-DD HH:mm')):
    ora = arrow.get(ora)
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

    impegnati = {}
    for persona in impegni:
        for impegno in impegni[persona]:
            if impegno.begin <= ora and impegno.end > ora:
                impegnati[persona] = impegno.description
                
    disponibilita = {persona: 'Non in servizio' for persona in orari_di_lavoro}

    for persona in di_turno:
        disponibilita[persona] = 'in servizio'

    for persona in impegnati:
        # una persona può avere più impegni, riposto la descrizione
        # del primo trovato
        disponibilita[persona] = impegnati[persona]
    
    print(disponibilita)
            
if __name__ == "__main__":
    if(len(sys.argv) < 3):
        print("""
        help: [nome_script] file_orari.or file_impegni.ics [timestamp "+%Y-%m-%dT%H:%m"]
        """)
    else:
        if(len(sys.argv) < 4):
            main(sys.argv[1], sys.argv[2])
        else:
            main(sys.argv[1], sys.argv[2], sys.argv[3])

import arrow
giorni_settimana = ['lun', 'mar', 'mer', 'gio', 'ven', 'sab', 'dom']

def load_orari(orari_file: str):
    """Carica la lista degli orari dal file `orari_file' e restituisce un
set {persona1: [lista_orari1], persona2: ...}"""
    
    # Carica il file orari_file e rompe la lista di readlines() in
    # chunck in base alle linee vuote
    orari_lines = open(orari_file).readlines()
    size = len(orari_lines) + 1
    idx_list = [idx + 1 for idx, val in
                enumerate(orari_lines) if val == '\n']
    persone = [orari_lines[i: j-1] for i, j in
               zip([0] + idx_list, 
                   idx_list + ([size] if idx_list[-1] != size else []))] 
    orari = {}
    # Implementa un parsing molto semplice a partire dalla lista
    # persone di prima, ogni elemento della lista è visto come una
    # persona, ogni persona ha come primo elemento il proprio nome
    # seguito da una serie di stringhe che definiscono una mappa
    # {'giorno': [[orario1] [orario2] ...]} alla fine viene fuori una
    # mappa che associa al nome di ogni persona il suo turno di lavoro
    for persona in persone:
        nome_persona = persona[0].replace('\n','').replace(':', '')
        orari.setdefault(nome_persona, {})
        # Dalla seconda entry in poi di ogni persona vengono definiti
        # i giorni lavorativi coi relativi turni
        for entry in persona[1:]:
            giorno_lavorativo = entry.split(': ')
            giorno = giorno_lavorativo[0].replace(':','').replace('\t','')
            # Dopo il ':' ci sono i vari turni indicati con la
            # sintassi inizio-fine inizio1-fine1 ecc.
            for turno in giorno_lavorativo[1].split(' '):
                list_turno = [ora.replace('\n', '') for ora in turno.split('-')]
                # Trick per aggiungere elementi al set
                if giorno in orari[nome_persona]:
                    orari[nome_persona][giorno].append(list_turno)
                else:
                    orari[nome_persona].setdefault(giorno,[])
                    orari[nome_persona][giorno].append(list_turno)
    return orari

# restituisce lista delle persone disponibili all'ora indicata secondo
# la mappa fornita da orari_di_lavoro
def interseca(orari_di_lavoro: set, ora):
    giorno = giorni_settimana[int(ora.format('d')) - 1]
    orari_giorno = []
    
    for persona in orari_di_lavoro:
        if giorno in orari_di_lavoro[persona]:
            orari_giorno.append([persona, orari_di_lavoro[persona][giorno]])

    disponibilita = {persona: False for persona in orari_di_lavoro}
    
    for persona in orari_giorno:
        nome_persona = persona[0].replace(':', '')
        orari_persona = persona[1]
        for turno in orari_persona:
            if len(turno) > 1:
                inizio_turno = arrow.get(ora.format('YYYY-MM-DDT') + turno[0])
                fine_turno = arrow.get(ora.format('YYYY-MM-DDT') + turno[1])
                if ora >= inizio_turno and ora < fine_turno:
                    disponibilita[nome_persona] = True

    disponibili = []
    for persona in disponibilita:
        if disponibilita[persona]:
            disponibili.append(persona)

    return disponibili

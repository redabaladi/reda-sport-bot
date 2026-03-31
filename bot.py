import requests
import json
from datetime import datetime

# LE TUE CHIAVI E LINK
API_KEY = '933a5e8f87b5a55a4632726a2df923d4'
FIREBASE_URL = "https://partite-live-default-rtdb.europe-west1.firebasedatabase.app/canali_tv.json"

# I campionati VIP (Serie A, Champions, Nazionali, ecc.)
VIP_LEAGUES = [135, 137, 140, 143, 39, 2, 3, 1, 4, 10, 21] 

def aggiorna_canali_veri():
    oggi = datetime.now().strftime('%Y-%m-%d')
    print(f"Inizio ricerca reale per le partite del: {oggi}")
    
    headers = {'x-apisports-key': API_KEY}
    url_fixtures = f"https://v3.football.api-sports.io/fixtures?date={oggi}"
    res = requests.get(url_fixtures, headers=headers).json()

    partite_in_tv = {}

    if 'response' not in res or not res['response']:
        print("Nessuna partita trovata oggi nell'API.")
        partite_in_tv["Oggi"] = "Nessuna partita in programma."
    else:
        partite_vip = [p for p in res['response'] if p['league']['id'] in VIP_LEAGUES]
        print(f"Trovate {len(partite_vip)} partite VIP oggi. Controllo i canali...")

        for p in partite_vip:
            fixture_id = p['fixture']['id']
            nome_partita = f"{p['teams']['home']['name']} - {p['teams']['away']['name']}"

            url_tv = f"https://v3.football.api-sports.io/fixtures/tv?fixture={fixture_id}"
            res_tv = requests.get(url_tv, headers=headers).json()

            if 'response' in res_tv and res_tv['response']:
                # Cerca i canali italiani
                canali_ita = [t['tv'] for t in res_tv['response'] if t.get('country', '').lower() == 'italy']
                
                if canali_ita:
                    partite_in_tv[nome_partita] = "📺 " + " e ".join(canali_ita)

        if not partite_in_tv:
            partite_in_tv["Nessun Match"] = "Nessun canale italiano comunicato per i big match di oggi."

    # Invia i dati a Firebase
    risposta_fb = requests.put(FIREBASE_URL, data=json.dumps(partite_in_tv))
    
    if risposta_fb.status_code == 200:
        print("✅ Successo! Firebase aggiornato con le partite VERE.")
    else:
        print("❌ Errore con Firebase:", risposta_fb.text)

if __name__ == "__main__":
    aggiorna_canali_veri()

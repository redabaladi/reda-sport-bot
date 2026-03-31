import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

API_KEY = '933a5e8f87b5a55a4632726a2df923d4'
FIREBASE_URL = "https://partite-live-default-rtdb.europe-west1.firebasedatabase.app/canali_tv.json"

# IL CERVELLO TRADUTTORE: Trasforma i nomi inglesi dell'API nei nomi usati dalle TV Italiane
TRADUZIONI = {
    "ITALY": "ITALIA",
    "BOSNIA & HERZEGOVINA": "BOSNIA",
    "SPAIN": "SPAGNA",
    "GERMANY": "GERMANIA",
    "FRANCE": "FRANCIA",
    "ENGLAND": "INGHILTERRA",
    "NETHERLANDS": "OLANDA",
    "PORTUGAL": "PORTOGALLO",
    "BELGIUM": "BELGIO",
    "CROATIA": "CROAZIA",
    "SWITZERLAND": "SVIZZERA"
}

def raschia_vero_internet():
    oggi = datetime.now().strftime('%Y-%m-%d')
    print("1. Guardo l'API per sapere chi gioca oggi...")
    
    url_fixtures = f"https://v3.football.api-sports.io/fixtures?date={oggi}"
    res = requests.get(url_fixtures, headers={'x-apisports-key': API_KEY}).json()
    
    partite_in_tv = {}
    if 'response' not in res or not res['response']:
        partite_in_tv["Oggi"] = "Nessuna partita in programma."
        requests.put(FIREBASE_URL, data=json.dumps(partite_in_tv))
        return

    print("2. Vado su INTERNET a leggere i siti italiani (SCRAPING)...")
    url_guida = "https://www.staseraintv.com/calcio_in_tv.html"
    headers_web = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        risposta_web = requests.get(url_guida, headers=headers_web)
        soup = BeautifulSoup(risposta_web.text, 'html.parser')
        testo_sito = soup.get_text(separator=" ", strip=True).upper()
        
        print("3. Traduco i nomi e incrocio col testo web...")
        for p in res['response']:
            # Nomi originali in inglese
            sq_casa_eng = p['teams']['home']['name'].upper()
            sq_trasf_eng = p['teams']['away']['name'].upper()
            nome_partita = f"{p['teams']['home']['name']} - {p['teams']['away']['name']}"
            
            # Nomi tradotti in italiano (se esistono nel dizionario, sennò usa l'originale)
            sq_casa_ita = TRADUZIONI.get(sq_casa_eng, sq_casa_eng)
            sq_trasf_ita = TRADUZIONI.get(sq_trasf_eng, sq_trasf_eng)
            
            if sq_casa_ita in testo_sito or sq_trasf_ita in testo_sito:
                indice = testo_sito.find(sq_casa_ita)
                if indice == -1:
                    indice = testo_sito.find(sq_trasf_ita)
                    
                inizio = max(0, indice - 100)
                fine = min(len(testo_sito), indice + 100)
                testo_vicino = testo_sito[inizio:fine]
                
                canali_trovati = []
                if "RAI 1" in testo_vicino or "RAI UNO" in testo_vicino: canali_trovati.append("Rai 1")
                elif "RAI 2" in testo_vicino or "RAI DUE" in testo_vicino: canali_trovati.append("Rai 2")
                elif "RAI" in testo_vicino: canali_trovati.append("Rai")
                if "DAZN" in testo_vicino: canali_trovati.append("DAZN")
                if "SKY SPORT" in testo_vicino or "SKY CALCIO" in testo_vicino or "SKY" in testo_vicino: canali_trovati.append("Sky Sport")
                if "CANALE 5" in testo_vicino or "MEDIASET" in testo_vicino: canali_trovati.append("Canale 5")
                if "ITALIA 1" in testo_vicino: canali_trovati.append("Italia 1")
                if "TV8" in testo_vicino: canali_trovati.append("TV8")
                if "NOVE" in testo_vicino: canali_trovati.append("Nove")
                if "SPORTITALIA" in testo_vicino: canali_trovati.append("Sportitalia")

                if canali_trovati:
                    canali_unici = list(set(canali_trovati))
                    partite_in_tv[nome_partita] = "📺 In Italia su: " + " e ".join(canali_unici)
                else:
                    partite_in_tv[nome_partita] = "📺 Partita menzionata in TV, canale esatto non identificato"

    except Exception as e:
        partite_in_tv["Errore"] = f"Errore: {e}"

    if not partite_in_tv:
        partite_in_tv["Oggi"] = "Nessun canale italiano trovato oggi."

    # 4. Invia i dati a Firebase
    requests.put(FIREBASE_URL, data=json.dumps(partite_in_tv))
    print("✅ Firebase aggiornato!")

if __name__ == "__main__":
    raschia_vero_internet()

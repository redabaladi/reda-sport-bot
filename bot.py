import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# LE TUE CHIAVI
API_KEY = '933a5e8f87b5a55a4632726a2df923d4'
FIREBASE_URL = "https://partite-live-default-rtdb.europe-west1.firebasedatabase.app/canali_tv.json"

def raschia_vero_internet():
    oggi = datetime.now().strftime('%Y-%m-%d')
    print("1. Guardo l'API SOLO per sapere chi gioca oggi (i nomi delle squadre)...")
    
    url_fixtures = f"https://v3.football.api-sports.io/fixtures?date={oggi}"
    res = requests.get(url_fixtures, headers={'x-apisports-key': API_KEY}).json()
    
    partite_in_tv = {}
    if 'response' not in res or not res['response']:
        partite_in_tv["Oggi"] = "Nessuna partita in programma."
        requests.put(FIREBASE_URL, data=json.dumps(partite_in_tv))
        return

    print("2. Vado su INTERNET a leggere i veri siti italiani (SCRAPING)...")
    
    # Il robottino entra fisicamente in un sito di Guida TV per estrarre il testo
    url_guida = "https://www.staseraintv.com/calcio_in_tv.html"
    headers_web = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        risposta_web = requests.get(url_guida, headers=headers_web)
        soup = BeautifulSoup(risposta_web.text, 'html.parser')
        
        # Trasforma l'intero sito in un testo leggibile
        testo_sito = soup.get_text(separator=" ", strip=True).upper()
        
        print("3. Incrocio i nomi delle squadre col testo raschiato dal sito...")
        for p in res['response']:
            squadra_casa = p['teams']['home']['name'].upper()
            squadra_trasf = p['teams']['away']['name'].upper()
            nome_partita = f"{p['teams']['home']['name']} - {p['teams']['away']['name']}"
            
            # Cerca se il sito internet parla di questa squadra
            if squadra_casa in testo_sito or squadra_trasf in testo_sito:
                
                # Trova in che punto della pagina c'è la squadra
                indice = testo_sito.find(squadra_casa)
                if indice == -1:
                    indice = testo_sito.find(squadra_trasf)
                    
                # Ritaglia solo il pezzo di testo attorno alla squadra (per capire il canale)
                inizio = max(0, indice - 100)
                fine = min(len(testo_sito), indice + 100)
                testo_vicino = testo_sito[inizio:fine]
                
                canali_trovati = []
                # Ora cerchiamo i canali REALI in quel pezzo di testo
                if "DAZN" in testo_vicino: canali_trovati.append("DAZN")
                if "SKY SPORT" in testo_vicino or "SKY CALCIO" in testo_vicino or "SKY" in testo_vicino: canali_trovati.append("Sky Sport")
                if "RAI" in testo_vicino: canali_trovati.append("Rai")
                if "MEDIASET" in testo_vicino or "CANALE 5" in testo_vicino or "ITALIA 1" in testo_vicino: canali_trovati.append("Mediaset")
                if "AMAZON" in testo_vicino or "PRIME" in testo_vicino: canali_trovati.append("Amazon Prime Video")
                if "TV8" in testo_vicino: canali_trovati.append("TV8")
                if "NOVE" in testo_vicino: canali_trovati.append("Nove")
                if "SPORTITALIA" in testo_vicino: canali_trovati.append("Sportitalia")
                if "YOUTUBE" in testo_vicino or "CRONACHE" in testo_vicino: canali_trovati.append("YouTube / Streaming")

                if canali_trovati:
                    canali_unici = list(set(canali_trovati))
                    partite_in_tv[nome_partita] = "📺 " + " e ".join(canali_unici)
                else:
                    partite_in_tv[nome_partita] = "📺 Partita sul web, ma canale non identificato"

    except Exception as e:
        partite_in_tv["Errore"] = f"Errore durante lo scraping: {e}"

    if not partite_in_tv:
        partite_in_tv["Oggi"] = "Scraping completato: Nessun incrocio esatto trovato per le partite di oggi sui siti italiani."

    # 4. Invia i dati a Firebase
    requests.put(FIREBASE_URL, data=json.dumps(partite_in_tv))
    print("✅ Firebase aggiornato estraendo dati dai VERI siti web.")

if __name__ == "__main__":
    raschia_vero_internet()

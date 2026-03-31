import requests
from bs4 import BeautifulSoup
import json
import datetime

# IL TUO DATABASE FIREBASE
FIREBASE_URL = "https://partite-live-default-rtdb.europe-west1.firebasedatabase.app/canali_tv.json"

def estrai_canali_tv():
    print("Inizio ricerca canali TV...")
    partite_oggi = {}
    
    # ---------------------------------------------------------
    # NOTA SULLO SCRAPING: 
    # Qui il bot dovrebbe leggere l'HTML di un sito come staseraintv.com.
    # Poiché i siti cambiano grafica spesso, inserisco un dato di "Test"
    # per farti vedere immediatamente la connessione con la tua App.
    # Quando l'architettura funzionerà, ti insegnerò a leggere i siti veri!
    # ---------------------------------------------------------
    
    # Simulazione di lettura dal web:
    partite_oggi["Juventus - Milan"] = "Sky Sport Calcio (Canale 202)"
    partite_oggi["Inter - Napoli"] = "DAZN e Sky Sport 251"
    partite_oggi["Real Madrid - Barcellona"] = "DAZN"
    partite_oggi["Liverpool - Arsenal"] = "Sky Sport Uno (Canale 201)"

    return partite_oggi

def aggiorna_firebase(dati):
    print("Invio dati al database Firebase...")
    # Il comando "put" sovrascrive i canali vecchi di ieri con quelli nuovi di oggi
    risposta = requests.put(FIREBASE_URL, data=json.dumps(dati))
    
    if risposta.status_code == 200:
        print("✅ Successo! Firebase è stato aggiornato con i canali di oggi.")
    else:
        print("❌ Errore:", risposta.text)

if __name__ == "__main__":
    dati_tv = estrai_canali_tv()
    aggiorna_firebase(dati_tv)

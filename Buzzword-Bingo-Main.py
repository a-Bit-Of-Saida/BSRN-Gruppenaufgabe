import os
import sys
import TermTk as ttk #importiert pyTermTk zum visualisieren
import random
from TermTk.TTkCore.cfg import TTkCfg
from TermTk.TTkCore.constant import TTkK
from TermTk.TTkCore.color import TTkColor  
from TermTk.TTkLayouts import TTkGridLayout, TTkLayout
from TermTk.TTkWidgets import TTkWidget
from TermTk.TTkWidgets.button import TTkButton
from TermTk.TTkWidgets.resizableframe import TTkResizableFrame
from datetime import datetime #importiert die Zeit
import logging #importiert eine bib zur Erstellung einer Log-Datei

spielername = input("Nenne deinen Namen:") # Spielername wird eingegeben vom User
roundfile = input("Nenne den Pfad der Buzzwords-Datei:") #Beispiel path: C:\Users\covrk\Documents\GitHub\BSRN-Gruppenaufgabe\Buzzwords-Datei.txt
roundfileOpener = open(roundfile, 'r')
# Speicherort der Logdatei
log_path = input("Nenne den Pfad des Log Dateien Speicherortes:")
# Anzahl der Zeilen und Spalten für die Button Grid
zeilen = int(input("Anzahl an Zeilen:"))
spalten = int(input("Anzahl an Spalten:"))

#Funktion zur Erstellung der Log-Datei
def create_log_file(player_name, log_directory):
    os.makedirs(log_directory, exist_ok=True)
    # Erstelle den Log-Dateinamen mit dem aktuellen Datum und dem Spielernamen
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    log_file_name = os.path.join(log_directory, f"log-{date_string}-{player_name}.txt")
    logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # Erste Info in der Log-Datei
    logging.info(f"Log-Datei für {player_name} erstellt.")

# Methode zum Lesen der Buzzwords aus der angegebenen Datei
def read_buzzword(roundfile):
    with open(roundfile, 'r', encoding='utf-8') as f:  # utf-8, damit man auch ÄÜÖ ausgeben kann auf den Buttons
        lines = f.readlines()
        return lines

buzzwords = read_buzzword(roundfile) #die Buzzwords sind die ausgelesenen Wörter der Datei mit dem var Namen roundfile

# Erstelle die Logdatei
create_log_file(spielername, log_path) # ruft die Log-File Methode auf und übergibt den Spielernamen sowie den Pfad zur Speicherung der Log_Datei

# Verändern des Button styles
class CustomTTkButton(TTkButton):
    def setBgColor(self, color):
        self.style()['default']['bg'] = TTkColor.fg(color) if color else None
        self.update()

# Erstellen des Fensters        
root = ttk.TTk()
window = ttk.TTkWindow(parent=root, pos=(1,1), size=(70,30), title="Buzzword Bingo :)")
winLayout = ttk.TTkGridLayout()
window.setLayout(winLayout)
used_buzzwords = set()

# Funktion zum Beenden des Spiels
def spiel_beenden():
    now = datetime.now() # Variable now nimmt den Wert der derzeitigen Zeit an
    logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Spiel durch den Beenden Button beendet") #in der Log_Datei als Beenden durch Button eingetragen
    sys.exit(0) #Beendet das Programm 

# Log-Datei Eintrag bei Anklicken eines Buttons
def log_buzzword(button):
    now = datetime.now() # Variable now nimmt den Wert der derzeitigen Zeit an
    button_text = button.text() 
    if button.isChecked(): # Wenn der Button angeklickt wurde, dann gib in der Log-Datei dies aus und davor noch die Zeit
        logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Button geklickt: {button_text}")
        button.setBgColor('#88ffff')
    else:
        logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Button rückgängig: {button_text}") # einmal das aus Zeile 62/63 rückgängig mit der gleichen Syntax
        button.setBgColor(None) 
    if close_button.isChecked(): # Wenn der Schließen-Button gedrückt wurde
        spiel_beenden()

# Setze die Buzzwords in die Knöpfe ein 
for i in range(zeilen):
    for j in range(spalten):
        buzzword = random.choice(buzzwords).strip()
        while buzzword in used_buzzwords:
            buzzword = random.choice(buzzwords).strip()
        used_buzzwords.add(buzzword)
        btn = CustomTTkButton(border=True, text=buzzword, font=("Times New Roman", 24), checkable=True)
        btn.clicked.connect(lambda b=btn: log_buzzword(b))
        winLayout.addWidget(btn, i, j)

close_button = CustomTTkButton(border=True, text="Spiel beenden", font=("Times New Roman", 24), checkable=True)
close_button.clicked.connect(spiel_beenden)  # Verbindet den Schließen-Button mit der Funktion zum Beenden des Spiels
winLayout.addWidget(close_button, zeilen+1, spalten+1)
root.mainloop()

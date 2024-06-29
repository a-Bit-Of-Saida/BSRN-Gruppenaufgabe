import datetime

# Funktion, um den Dateinamen zu generieren
def generate_filename(player_number):
    now = datetime.datetime.now()
    # Dateiformat erstellen: YYYY-MM-DD-HH-MM-SS-bingo-SpielerNummer.txt
    filename = f"{now.year:04d}-{now.month:02d}-{now.day:02d}-{now.hour:02d}-{now.minute:02d}-{now.second:02d}-bingo-{player_number}.txt"
    return filename

# Beispielaufruf der Funktion mit SpielerNummer = 1
player_number = 1
log_filename = generate_filename(player_number)
print("Generierte Dateiname:", log_filename, "Start des Spiels")

#Zum Daten einspeichern für die Zukunft
# with open(log_filename, 'w') as file:
#     file.write("Hier sind die Bingo-Spielinformationen für Spieler 1...")
#import textual
score_Spieler1 = 0
score_Spieler2 = 0
spielerName = input("Wie heißt du? ")
print("Willkommen", spielerName, "zu BUZZWORD")
#Einlesen der Buzzwords-Datei
# Einlesen der Buzzwords-Datei
print("Nenne den Namen der Datei:") #C:/Users/covrk/Documents/GitHub/BSRN-Gruppenaufgabe/Buzzwords.txt
roundfile = input()
roudnfileOpener = open(roundfile, 'r') #Variabeln umbenennen!

#Start des Spiels
print("Willkommen zum Buzzword-Bingo")
print("Nenne ein Wort:")
wort = input()

#Überprüfung ob das Wort in der Datei ist
if wort in roudnfileOpener.read():
    print("Dein Wort befindet sich in der Datei")
    score_Spieler1 = +1
    print("Der Score beträgt: ", score_Spieler1)
    roudnfileOpener.close()
else:
    print("Dieses Buzzword ist leider nicht dabei")



import os
import sys
import random
import time
from datetime import datetime
import logging
import TermTk as ttk  # Importiert pyTermTk zum Visualisieren
from TermTk.TTkCore.color import TTkColor  
from TermTk.TTkWidgets.button import TTkButton


def create_log_file(player_name: str, log_directory: str, zeilen: int, spalten: int):
    os.makedirs(log_directory, exist_ok=True)
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    log_file_name = os.path.join(log_directory, f"log-{date_string}-{player_name}.txt")
    logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info(f"Log-Datei für {player_name} erstellt.")
    logging.info(f"Zeilen: {zeilen}, Spalten: {spalten}")

def read_buzzword(roundfile: str):
    with open(roundfile, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        return lines

class CustomTTkButton(TTkButton):
    def setBgColor(self, color):
        self.style()['default']['bg'] = TTkColor.fg(color) if color else None
        self.update()

def spiel_beenden():
    now = datetime.now()
    logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Spiel durch den Beenden Button beendet")
    sys.exit(0)

def log_buzzword(button, zeilen, spalten):
    now = datetime.now()
    button_text = button.text()
    if button.isChecked():
        logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Button geklickt: {button_text}")
        button.setBgColor('#88ffff')
    else:
        logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Button rückgängig: {button_text}")
        button.setBgColor(None)
    if check_win(zeilen, spalten):
        gewonnen_animation()

def check_win(zeilen, spalten):
    for i in range(zeilen):
        if all(buttons[i][j].isChecked() for j in range(spalten)):
            return True
    for j in range(spalten):
        if all(buttons[i][j].isChecked() for i in range(zeilen)):
            return True
    if all(buttons[i][i].isChecked() for i in range(min(zeilen, spalten))):
        return True
    if all(buttons[i][spalten-1-i].isChecked() for i in range(min(zeilen, spalten))):
        return True
    return False

def gewonnen_animation():
    text = "SIE HABEN GEWONNEN"
    iterations = 3
    delay = 0.05

    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    h = 50
    w = 160
    x = w // 2 - len(text) // 2

    try:
        for a in range(iterations):
            clear_screen()
            for i in range(h):
                clear_screen()
                for j in range(i, i + h):
                    if j < h:
                        print(' ' * x + text)
                time.sleep(delay)

        time.sleep(1)

    except KeyboardInterrupt:
        pass

    spiel_beenden()


def main(spielername: str, roundfile: str, log_path: str, zeilen: int, spalten: int):
    buzzwords = read_buzzword(roundfile)
    create_log_file(spielername, log_path, zeilen, spalten)
    root = ttk.TTk()
    window = ttk.TTkWindow(parent=root, pos=(1, 1), size=(70, 30), title="Buzzword Bingo :)")
    winLayout = ttk.TTkGridLayout()
    window.setLayout(winLayout)
    used_buzzwords = set()
    global buttons
    buttons = [[None for _ in range(spalten)] for _ in range(zeilen)]
    
    for i in range(zeilen):
        for j in range(spalten):
            if zeilen % 2 != 0 and spalten % 2 != 0 and i == zeilen // 2 and j == spalten // 2:
                btn = CustomTTkButton(border=True, text="Joker", font=("Times New Roman", 24), checkable=True, checked=True)
                btn.setBgColor(color='#ff88ff')
                winLayout.addWidget(btn, i, j)
                buttons[i][j] = btn
            else:
                buzzword = random.choice(buzzwords).strip()
                while buzzword in used_buzzwords:
                    buzzword = random.choice(buzzwords).strip()
                used_buzzwords.add(buzzword)
                btn = CustomTTkButton(border=True, text=buzzword, font=("Times New Roman", 24), checkable=True)
                btn.clicked.connect(lambda b=btn: log_buzzword(b, zeilen, spalten))
                winLayout.addWidget(btn, i, j)
                buttons[i][j] = btn

    close_button = CustomTTkButton(border=True, text="Spiel beenden", font=("Times New Roman", 24), checkable=True)
    close_button.clicked.connect(spiel_beenden)
    winLayout.addWidget(close_button, zeilen, spalten - 1)
    root.mainloop()

if __name__ == "__main__":
    main()

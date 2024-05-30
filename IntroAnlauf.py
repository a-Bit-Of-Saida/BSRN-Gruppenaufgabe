import TermTk as ttk
from TermTk.TTkWidgets import TTkWidget
from TermTk.TTkWidgets.button import TTkButton
from TermTk.TTkWidgets.window import TTkWindow
from TermTk.TTkLayouts import TTkGridLayout


def show_instructions(root):
    root.quit()
    instructions = """
    Spielanleitung:
    1. Dies ist ein Buzzword Bingo-Spiel.
    2. Drücke auf die Buzzwords, wenn sie während des Spiels erwähnt werden.
    3. Wenn du eine vollständige Zeile, Spalte oder Diagonale markiert hast, gewinnst du.
    4. Viel Spaß!
    """
    new_root = ttk.TTk()
    window = TTkWindow(parent=new_root, pos=(1, 1), size=(80, 20), title="Spielanleitung")
    layout = ttk.TTkGridLayout()
    window.setLayout(layout)
    label = TTkLabel(text=instructions, maxWidth=78)
    layout.addWidget(label, 0, 0)
    back_button = CustomTTkButton(border=True, text="Zurück", maxWidth=20)
    back_button.clicked.connect(lambda: (new_root.quit(), show_intro()))
    layout.addWidget(back_button, 1, 0)
    new_root.mainloop()

# Intro-Funktion
def show_intro():
    root = ttk.TTk()
    window = TTkWindow(parent=root, pos=(1, 1), size=(50, 20), title="Buzzword Bingo Intro")
    layout = ttk.TTkGridLayout()
    window.setLayout(layout)

    play_button = CustomTTkButton(border=True, text="Play", maxWidth=20)
    play_button.clicked.connect(lambda: (root.quit(), start_game()))
    layout.addWidget(play_button, 0, 0)

    instructions_button = CustomTTkButton(border=True, text="Spielanleitung", maxWidth=20)
    instructions_button.clicked.connect(lambda: show_instructions(root))
    layout.addWidget(instructions_button, 1, 0)

    exit_button = CustomTTkButton(border=True, text="Exit", maxWidth=20)
    exit_button.clicked.connect(lambda: (root.quit(), sys.exit(0)))
    layout.addWidget(exit_button, 2, 0)

    root.mainloop()
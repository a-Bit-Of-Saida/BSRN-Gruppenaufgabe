import curses
import random
import sys
import time
import os
import logging
import datetime
import posix_ipc  # type: ignore

clients = []
QUEUE_SERVER = "/serverQueue"

def intro_menu(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()

    menu_options = ["Start", "Bedienung", "Exit"]
    current_option = 0
    spacing = 2  # Abstand zwischen den Menüoptionen

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        for idx, option in enumerate(menu_options):
            x = width // 2 - len(option) // 2
            y = height // 2 - (len(menu_options) * spacing) // 2 + idx * spacing
            if idx == current_option:
                stdscr.addstr(y, x, option, curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, option)

        key = stdscr.getch()

        if key == curses.KEY_UP and current_option > 0:
            current_option -= 1
        elif key == curses.KEY_DOWN and current_option < len(menu_options) - 1:
            current_option += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_option == 0:
                return "start"
            elif current_option == 1:
                show_instructions(stdscr)
            elif current_option == 2:
                return "exit"

def show_instructions(stdscr):
    instructions = [
        "Willkommen zum Bingo-Spiel!",
        "Bedienung:",
        "  - Verwenden Sie die Pfeiltasten, um sich auf dem Spielfeld zu bewegen.",
        "  - Drücken Sie die Eingabetaste, um ein Feld auszuwählen oder zu deaktivieren.",
        "  - Drücken Sie die 'Bingo'-Taste, wenn Sie ein Bingo haben.",
        "Drücken Sie eine beliebige Taste, um zum Menü zurückzukehren."
    ]
    
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    for idx, line in enumerate(instructions):
        x = width // 2 - len(line) // 2
        y = height // 2 - len(instructions) // 2 + idx
        stdscr.addstr(y, x, line)

    stdscr.refresh()
    stdscr.getch()

def create_log_file(player_name: str, log_directory: str, zeilen: int, spalten: int):
    os.makedirs(log_directory, exist_ok=True)
    now = datetime.datetime.now()
    date_string = now.strftime("%Y-%m-%d-%H-%M-%S")
    log_file_name = os.path.join(log_directory, f"log-{date_string}-bingo-{player_name}.txt")
    logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info(f"Log-Datei für {player_name} erstellt.")
    logging.info(f"Größe des Spielfelds: Zeilen: {zeilen}, Spalten: {spalten}")
    logging.info(f"Start des Spiels.")
    
def log_buzzword(button, row, col, app):
    button_text = button.label
    if button.pressed:
        logging.info(f"Button geklickt: {button_text} (Zeile: {row+1}, Spalte: {col+1})")
    else:
        logging.info(f"Button rückgängig: {button_text} (Zeile: {row+1}, Spalte: {col+1})")

def spiel_beenden():
    logging.info("Ende des Spiels")
    sys.ecit(0)

def run_game(stdscr, player_name, zeilen, spalten, roundfile, log_path, game_state=None):
    if curses.LINES < 20 or curses.COLS < 80:
        raise Exception("Terminal window is too small. Please resize to at least 80x20.")

    app = ButtonGridApp(stdscr, player_name, zeilen, spalten, roundfile)
    if game_state:
        app.restore_game_state(game_state)
    create_log_file(player_name, log_path, zeilen, spalten)

    # Start a thread to listen for win messages
    listener_thread = threading.Thread(target=message_listener, args=(app, player_name))
    listener_thread.daemon = True
    listener_thread.start()

    # Setup signal handler for window resize
    signal.signal(signal.SIGWINCH, lambda signum, frame: handle_resize(signum, frame, app))

    app.run(stdscr)


def message_listener(app, player_name):
    client_queue_name = f"/client_{player_name}"
    queue_client = posix_ipc.MessageQueue(client_queue_name)
    try:
        while True:
            message, _ = queue_client.receive()
            content = message.decode()
            if content.endswith("hat gewonnen!"):
                winner_name = content.split()[0]
                print(f"{winner_name} hat gewonnen! Exiting the game.")
                logging.info(f"{winner_name} hat gewonnen!")  # Log the winner
                app.gewonnen_animation(winner_name)
                # Log before exiting curses mode
                logging.shutdown()
                # Properly close resources and exit
                curses.endwin()  # Exit curses mode
                cleanup()  # Clean up all resources
            else:
                # Log other messages if needed
                logging.info(content)
    except Exception as e:
        logging.error(f"Error receiving message: {str(e)}")  # Use logging for error messages as well
        logging.shutdown()
        cleanup()  # Ensure cleanup is called on exception or termination


def run_game_wrapper(stdscr):
    run_game(stdscr, player_name, zeilen, spalten, roundfile, log_path)

def handle_win_message(win_message):
    queue_server = posix_ipc.MessageQueue(QUEUE_SERVER)
    for client_queue_name in clients:
        try:
            client_queue = posix_ipc.MessageQueue(client_queue_name)
            client_queue.send(win_message.encode())
        except posix_ipc.ExistentialError:
            print(f"Error: Could not open client queue '{client_queue_name}'")
    queue_server.close()
    queue_server.unlink()
    close_game()

def handle_resize(signum, frame, app):
    app.handle_resize()

def main(player):
    global player_name, zeilen, spalten, roundfile, log_path
    player_name = player

    try:
        client_queue_name = f"/client_{player_name}"
        clients.append(client_queue_name)
        queue_server = posix_ipc.MessageQueue(QUEUE_SERVER)
        queue_client = posix_ipc.MessageQueue(client_queue_name, posix_ipc.O_CREAT)

        join_message = f"JOIN|{client_queue_name}"
        queue_server.send(join_message.encode())
        print(f"Sent join message to server: {join_message}")

        while True:
            message, _ = queue_client.receive()
            content = message.decode()
            print(f"Received message: {content}")
            if content == "All players joined. Game can start":
                print("Game can start.")
                time.sleep(3)

                def run_game_wrapper(stdscr):
                    if curses.LINES < 20 or curses.COLS < 80:
                        print("Terminal window is too small. Please resize to at least 80x20.")
                        return
                    run_game(stdscr, player_name, zeilen, spalten, roundfile, log_path)

                result = curses.wrapper(intro_menu)
                if result == "start":
                    curses.wrapper(run_game_wrapper)
                elif result == "exit":
                    cleanup()
                    sys.exit(0)
                break
            elif content.endswith("hat gewonnen!"):
                print(f"{content} - Exiting the game...")
                curses.endwin()
                sys.exit(0)
            else:
                params_list = content.split('|')
                if len(params_list) == 5:
                    roundfile = params_list[0]
                    log_path = params_list[1]
                    zeilen = int(params_list[2])
                    spalten = int(params_list[3])
                    max_players = int(params_list[4])
                    print(f"Received parameters from server:")
                    print(f"Roundfile: {roundfile}")
                    print(f"Log Path: {log_path}")
                    print(f"Zeilen: {zeilen}")
                    print(f"Spalten: {spalten}")
                else:
                    print("Received invalid parameters from server.")
                    sys.exit(1)

    except posix_ipc.ExistentialError as e:
        print(f"Error: Message queue '{QUEUE_SERVER}' or '{client_queue_name}' does not exist.")
    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        cleanup()
        
def close_game():
    print("Game closed, exiting in 5 seconds...")
    time.sleep(3)
    sys.exit(0)

class Button:
    def __init__(self, label, selected=False):
        self.label = label
        self.selected = selected
        self.pressed = False

    def toggle_pressed(self):
        self.pressed = not self.pressed
        print(f"Button {self.label} pressed: {self.pressed}")
        
    def set_pressed(self, pressed):
        self.pressed = pressed

class ButtonGridApp:
    def __init__(self, stdscr, player_name, zeilen, spalten, roundfile):
        self.stdscr = stdscr
        self.rows = zeilen
        self.columns = spalten
        self.button_width = 35
        self.button_height = 5
        self.buttons = []
        self.selected_button_index = 0
        self.player_name = player_name
        self.roundfile = roundfile
        self.game_state = None
        self.bingo_reached = False
        self.initialize_buttons()
    
    def handle_resize(self):
        curses.endwin()
        self.stdscr.refresh()
        self.stdscr.clear()
        self.draw_buttons()
    
    def broadcast_win(self):
            win_message = f"{self.player_name} hat gewonnen!"
            logging.info("Ende des Spiels")
            try:
                queue_server = posix_ipc.MessageQueue(QUEUE_SERVER)
                queue_server.send(win_message.encode())
                queue_server.close()
            except posix_ipc.ExistentialError:
                print(f"Error: Could not open server queue '{QUEUE_SERVER}'")

            # Send the win message to all clients
            for client_queue_name in clients:
                try:
                    client_queue = posix_ipc.MessageQueue(client_queue_name)
                    client_queue.send(win_message.encode())
                    client_queue.close()
                except posix_ipc.ExistentialError:
                    print(f"Error: Could not open client queue '{client_queue_name}'")

            time.sleep(3)
            queue_server.unlink()
            time.sleep(5)
            close_game()

    def draw_player_name(self):
        player_label = f"Spieler: {self.player_name}"
        start_y = 0  # Zeile direkt über dem Buttonfeld
        start_x = (curses.COLS - len(player_label)) // 2  # Zentriert über die Breite des Terminals
        self.stdscr.addstr(start_y, start_x, player_label, curses.A_BOLD)
        self.stdscr.refresh()
        
    def toggle_button_pressed(self, index):
        button = self.buttons[index]
        # Umkehrung des pressed-Status
        button.set_pressed(not button.pressed)
        row, col = divmod(index, self.columns)
    
    def resize(self):
        curses.endwin()
        self.stdscr.refresh()
        self.draw_buttons()
        
    def handle_resize(signum, frame, app):
        app.resize()
    
    def get_game_state(self):
        # Return a dictionary representing the current game state
        return {
            'buttons': [(button.label, button.pressed) for button in self.buttons],
            'selected_button_index': self.selected_button_index
        }
        
    def restore_game_state(self, game_state):
        # Restore the game state from the given dictionary
        for i, (label, pressed) in enumerate(game_state['buttons']):
            self.buttons[i].label = label
            self.buttons[i].pressed = pressed
        self.selected_button_index = game_state['selected_button_index']

    def initialize_buttons(self):
        with open(self.roundfile, 'r') as f:
            words = [line.strip() for line in f.readlines()]

        if len(words) < self.rows * self.columns:
            print(f"Not enough words in roundfile ({len(words)}) to fill the grid ({self.rows}x{self.columns}).")
            sys.exit(1)

        button_labels = random.sample(words, self.rows * self.columns)
        for label in button_labels:
            button = Button(label)
            self.buttons.append(button)
        
        if self.rows % 2 == 1 and self.columns % 2 == 1:
            middle_index = self.rows * self.columns // 2
            self.buttons[middle_index].pressed = True
            self.buttons[middle_index].label = "JOKER"
        self.bingo_button = Button("Bingo")
        self.buttons.append(self.bingo_button)

    def run(self, stdscr):
            self.stdscr = stdscr
            curses.curs_set(0)
            curses.start_color()
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)
            curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)

            self.draw_player_name()
            self.buttons[self.selected_button_index].selected = True
            self.draw_buttons()
            while True:
                key = self.stdscr.getch()
                if key == curses.KEY_RESIZE:
                    self.handle_resize()
                elif key == curses.KEY_UP and self.selected_button_index >= self.columns:
                    self.update_selected_button(self.selected_button_index - self.columns)
                elif key == curses.KEY_DOWN and self.selected_button_index < len(self.buttons) - self.columns:
                    self.update_selected_button(self.selected_button_index + self.columns)
                elif key == curses.KEY_LEFT and self.selected_button_index % self.columns > 0:
                    self.update_selected_button(self.selected_button_index - 1)
                elif key == curses.KEY_RIGHT and self.selected_button_index % self.columns < self.columns - 1:
                    self.update_selected_button(self.selected_button_index + 1)
                elif key == 10:  # Enter key
                    if self.selected_button_index == len(self.buttons) - 1:  # BINGO button
                        if self.check_for_win():
                            self.broadcast_win()
                            self.gewonnen_animation(self.player_name)
                            return
                    else:
                        self.toggle_button_pressed(self.selected_button_index)

                self.draw_buttons()

    def toggle_button_pressed(self, index):
        button = self.buttons[index]
        button.toggle_pressed()
        row, col = divmod(index, self.columns)

    def draw_buttons(self):
        self.stdscr.clear()  # Clear the entire screen
        try:
            self.draw_player_name()  # Draw the player name label first

            max_y, max_x = self.stdscr.getmaxyx()
            button_area_height = self.rows * (self.button_height + 1) + 2
            button_area_width = self.columns * (self.button_width + 2) + 1

            if button_area_height > max_y or button_area_width > max_x:
                error_message = "Terminal window is too small. Please resize to at least {button_area_width}x{button_area_height}."
                self.stdscr.addstr(0, 0, error_message)
                self.stdscr.refresh()
                return

            for r in range(self.rows):
                for c in range(self.columns):
                    index = r * self.columns + c
                    button = self.buttons[index]

                    # Calculate position
                    start_y = r * (self.button_height + 1) + 2  # Add 2 to account for the label height
                    start_x = c * (self.button_width + 2) + 1

                    if start_y >= max_y or start_x + self.button_width >= max_x:
                        continue  # Skip drawing if the button exceeds terminal bounds

                    if button.selected:
                        if button.pressed:
                            self.stdscr.addstr(start_y, start_x, f"> [{button.label}] <", curses.color_pair(2))
                        else:
                            self.stdscr.addstr(start_y, start_x, f"> {button.label} <", curses.color_pair(1))
                    else:
                        if button.pressed:
                            self.stdscr.addstr(start_y, start_x, f"[{button.label}]", curses.color_pair(2))
                        else:
                            self.stdscr.addstr(start_y, start_x, button.label)

            # Highlight the "Bingo" button when it is selected
            bingo_start_y = self.rows * (self.button_height + 1) + 2
            bingo_start_x = 1
            if bingo_start_y < max_y and bingo_start_x + len("Bingo") < max_x:
                if self.selected_button_index == len(self.buttons) - 1:
                    self.stdscr.addstr(bingo_start_y, bingo_start_x, "Bingo", curses.A_BOLD | curses.color_pair(1))
                else:
                    self.stdscr.addstr(bingo_start_y, bingo_start_x, "Bingo", curses.A_BOLD | curses.color_pair(3))

        except curses.error as e:
            print(f"Error drawing buttons: {e}")
        
        self.stdscr.refresh()  # Refresh the screen to apply changes

    def check_for_win_and_register(self):
        if self.check_for_win():
            self.broadcast_win()
            
    def update_selected_button(self, new_index):
        self.buttons[self.selected_button_index].selected = False
        self.selected_button_index = new_index
        self.buttons[self.selected_button_index].selected = True

    def check_for_win(self):
        # Check for horizontal wins
        for r in range(self.rows):
            row_buttons = self.buttons[r * self.columns:(r + 1) * self.columns]
            if all(button.pressed for button in row_buttons):
                self.bingo_reached = True
                return True
    
        # Check for vertical wins
        for c in range(self.columns):
            col_buttons = [self.buttons[r * self.columns + c] for r in range(self.rows)]
            if all(button.pressed for button in col_buttons):
                self.bingo_reached = True
                return True
    
        # Check for diagonal wins
        diagonal_buttons = [self.buttons[i * self.columns + i] for i in range(self.rows)]
        if all(button.pressed for button in diagonal_buttons):
            self.bingo_reached = True
            return True
    
        diagonal_buttons = [self.buttons[i * self.columns + self.columns - i - 1] for i in range(self.rows)]
        if all(button.pressed for button in diagonal_buttons):
            self.bingo_reached = True
            return True
    
        return False
        
    def gewonnen_animation(self, spieler_name):
        def clear_screen():
            os.system('cls' if os.name == 'nt' else 'clear')
        text = f"Congratulations, {spieler_name} won!"
        stars = "*" * 20
        win_message = f"\n{stars}\n{text}\n{stars}\n"

        try:
            for _ in range(2):
                for i in range(len(win_message)):
                    clear_screen()
                    print(win_message[i:])
                    time.sleep(0.1)

            # Add a delay after the animation to allow the user to see it
            time.sleep(3)  # Adjust the duration as needed

        except KeyboardInterrupt:
            pass

        # Ensure the screen is cleared and curses mode is exited before exiting
        curses.endwin()
        spiel_beenden()  # This is your method to cleanly exit the game

    def cleanup():
        for client_queue_name in clients:
            try:
                client_queue = posix_ipc.MessageQueue(client_queue_name)
                client_queue.close()
                client_queue.unlink()
            except posix_ipc.ExistentialError:
                pass  # Ignore if queue does not exist

        try:
            queue_server = posix_ipc.MessageQueue(QUEUE_SERVER)
            queue_server.close()
            queue_server.unlink()
        except posix_ipc.ExistentialError:
            pass  # Ignore if queue does not exist

        curses.endwin()  # Ensure the curses window is properly closed
        sys.exit(0)  # Exit the program with success status
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <player_name>")
        sys.exit(1)
    player_name = sys.argv[1]
    try:
        main(player_name)
    finally:
        cleanup()


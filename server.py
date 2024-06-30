import posix_ipc # type: ignore
import sys

# Name der POSIX Message Queue für die Kommunikation mit Clients
QUEUE_SERVER = "/serverQueue"

def wait_for_player_join(queue_server, roundfile, log_path, zeilen, spalten, max_players):
    player_count = 0
    clients = []
    try:
        while player_count < max_players:
            message, _ = queue_server.receive()
            message_str = message.decode()
            if message_str.startswith("JOIN|"):
                client_queue_name = message_str.split("|")[1]
                print(f"Client joined: {client_queue_name}")
                clients.append(client_queue_name)
                player_count += 1
                send_game_params(client_queue_name, roundfile, log_path, zeilen, spalten, max_players)
            else:
                print(f"Invalid join message received: {message_str}")

        # Notify all clients that the game can start
        start_message = "All players joined. Game can start"
        notify_all_clients(clients, start_message)
        # Loop to receive win messages from clients
        while True:
            message, _ = queue_server.receive()
            message_str = message.decode()
            print(f"Received message from client: {message_str}")
            if message_str.endswith("hat gewonnen!"):
                handle_win_message(message_str, clients)
                queue_server.close() #queue nicht schließen sonst kommt nach dem Win dieser Fehler: Message queue '/serverQueue' does not exist.
                break

    except KeyboardInterrupt:
        print("Server stopped.")
    finally:
        try:
            queue_server.close()
            # Do not unlink here, unlink only when all clients have exited
        except posix_ipc.ExistentialError:
            pass
    
def send_game_params(client_queue_name, roundfile, log_path, zeilen, spalten, max_players):
    try:
        client_queue = posix_ipc.MessageQueue(client_queue_name)
        parameters = f"{roundfile}|{log_path}|{zeilen}|{spalten}|{max_players}"
        client_queue.send(parameters.encode())
        client_queue.close()
        print(f"Parameters sent to {client_queue_name}")
    except posix_ipc.ExistentialError:
        print(f"Failed to open client queue '{client_queue_name}'")
        
def main(roundfile, log_path, zeilen, spalten, max_players):
    try:
        # Attempt to create or open the message queue
        try:
            queue_server = posix_ipc.MessageQueue(QUEUE_SERVER, posix_ipc.O_CREAT)
        except posix_ipc.ExistentialError:
            queue_server = posix_ipc.MessageQueue(QUEUE_SERVER)

        wait_for_player_join(queue_server, roundfile, log_path, zeilen, spalten, max_players)
    except posix_ipc.ExistentialError:
        print(f"Message queue '{QUEUE_SERVER}' does not exist.")
        sys.exit(1)

def handle_win_message(win_message, clients):
    # Broadcast win message to all connected clients
    notify_all_clients(clients, win_message)
    print(f"Spieler: {win_message}!")

def notify_all_clients(clients, message):
    for client_queue_name in clients:
        try:
            client_queue = posix_ipc.MessageQueue(client_queue_name)
            client_queue.send(message.encode())
            client_queue.close()
            print(f"Message '{message}' sent to {client_queue_name}")
        except posix_ipc.ExistentialError:
            print(f"Failed to open client queue '{client_queue_name}'")
        
def is_valid_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    usage = """
    Nutze: server.py <roundfile_path> <log_path> <zeilen> <spalten> <max_players>

    Parameter:
      <roundfile_path>:   Pfad zu den Buzzwords dieser Runde.
      <log_path>:         Pfad in der die Log-Datei/Dateien gespeichert werden.
      <zeilen>:           Anzahl an Zeilen für das Bingofeld.
      <spalten>:          Anazhl an Spalten für das Bingofeld.
      <max_players>:      Maximale Anzahl an Spielern dieser Runde.

    Beispiel:
      python3 server.py Buzzwords-Datei.txt /path/to/logs 10 10 4
    """

    if len(sys.argv) == 6:
        roundfile = sys.argv[1]
        log_path = sys.argv[2]
        zeilen = sys.argv[3]
        spalten = sys.argv[4]
        max_players = sys.argv[5]

        # Validate zeilen, spalten, max_players inputs
        if not is_valid_int(zeilen):
            print("Bitte gib für 'zeilen' eine ganze Zahl ein.")
            sys.exit(1)
        if not is_valid_int(spalten):
            print("Bitte gib für 'spalten' eine ganze Zahl ein.")
            sys.exit(1)
        if not is_valid_int(max_players):
            print("Bitte gib für 'max_players' eine ganze Zahl ein.")
            sys.exit(1)

        # Convert zeilen, spalten, max_players to integers
        zeilen = int(zeilen)
        spalten = int(spalten)
        max_players = int(max_players)

        main(roundfile, log_path, zeilen, spalten, max_players)
    else:
        print(usage.strip())

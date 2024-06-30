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
            else:
                print(f"Invalid join message received: {message_str}")

        # Notify all clients that the game can start
        start_message = "All players joined. Game can start"

        # Loop to receive win messages from clients
        while True:
            message, _ = queue_server.receive()
            message_str = message.decode()
            print(f"Received message from client: {message_str}")
            if message_str.endswith("hat gewonnen!"):
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
        
if __name__ == "__main__":
    if len(sys.argv) == 6:
        roundfile = sys.argv[1]
        log_path = sys.argv[2]
        zeilen = sys.argv[3]
        spalten = sys.argv[4]
        max_players = sys.argv[5]
        main(roundfile, log_path, zeilen, spalten, max_players)
    else:
        print("Usage: server.py <roundfile_path> <log_path> <zeilen> <spalten> <max_players>")

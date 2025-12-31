# IoT Bot & Controller (C&C) System

This is a final project for Introduction to Cybersecurity project held by CVUT.
It implements a modular, encrypted Command and Control (C&C) system using the **MQTT** protocol, consisting of a **Bot** (running on a Linux target) and a **Controller** (used by the admin to send commands).

## 1. Requirements

The project is written in Python 3. It uses two external libraries for networking and security.

### `requirements.txt`

```text
paho-mqtt==1.6.1
cryptography==41.0.0

```

---

## 2. Custom C&C Communication Protocol

### Encryption & Loopback Prevention
* **Mechanism:** Symmetric encryption using **AES-128 in CBC mode** via the `cryptography.fernet` module.
* **Loopback Protection:** Since both parties use the same topic, a plaintext prefix is added to the data **before** encryption:
    * **`C:`**: Prepended by the Controller for all outgoing **Commands**.
    * **`R:`**: Prepended by the Bot for all outgoing **Responses**.
* **Noise Filtering:** Since the system uses a public broker, it is designed to **silently ignore** any messages that fail decryption (e.g., traffic from other users). This prevents the terminal from being flooded with decryption errors.

### Topic Structure
* `sensors`: The **unified topic** used for both commands and responses. Both the Bot and the Controller publish to and subscribe from this single topic.

### Command Set

| Command | Parameter | Internal Marker | Description |
| --- | --- | --- | --- |
| `Ping the bot` | None | `C:PING` | Bot responds with `R:BOT_STATUS: ONLINE` |
| `Users currently logged in` | None | `C:GET_USERS` | Returns output of the `w` command |
| `User´s ID` | None | `C:GET_ID` | Returns output of the `id` command |
| `List Dir` | Directory Path | `C:LS:<path>` | Returns a directory listing |
| `Get File` | File Path | `C:GET_FILE:<path>` | Bot uploads file via Base64 stream |
| `Exec Binary` | Binary Path | `C:EXEC:<path>` | Executes the specified binary |
| `Exit` | None | N/A | Closes the local Controller interface; Bot remains active. |

---

## 3. Installation instructions - How to run

**Prerequisite:** In case of needing to run virtual Python environment, run these command first:
`python3 -m venv venv`
`source venv/bin/activate`

1. **Install dependencies:** `pip install -r requirements.txt`
2. **Start the Bot:** `python3 bot.py`
3. **Start the Controller:** `python3 controller.py`

> **Note:** The shared communication on the `sensors` topic is fully encrypted. Even though both devices see all traffic, they can only decrypt and act on messages intended for them.

For a real production system, you should generate a unique key by running this command (instead of the one in the security.py):
`python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key())"`

---

## 4. How to Run in Docker

The project is containerized to ensure a consistent environment for the Linux system utilities.

### File Structure

Ensure your directory contains the following files:

* `bot.py`, `controller.py`, `security.py`, `requirements.txt`
* `Dockerfile.bot`, `Dockerfile.controller`, `docker-compose.yml` (These are necessary only if you want to run them in docker)

### Docker Configuration Files
In docker, do not forget to enable "Enable host networking" in Settings/Resources/Network in order for the the controller and bot being able to communicate.
Then in the repository folder, create these files with thier contents.
After that, you can control the docker with the commands provided in the Execution Steps

**Dockerfile.bot**

```dockerfile
FROM python:3.11-slim
# Install system utilities (ps, w, id)
RUN apt-get update && apt-get install -y procps coreutils && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot.py security.py ./
CMD ["python", "bot.py"]

```

**Dockerfile.controller**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY controller.py security.py ./
ENV PYTHONUNBUFFERED=1
CMD ["python", "controller.py"]

```

**docker-compose.yml**

```yaml
version: '3.8'
services:
  bot:
    build:
      context: .
      dockerfile: Dockerfile.bot
    restart: always    
    dns:
      - 8.8.8.8
    environment:
      - PYTHONUNBUFFERED=1

  controller:
    build:
      context: .
      dockerfile: Dockerfile.controller
    stdin_open: true
    tty: true
    depends_on:
      - bot    
    dns:
      - 8.8.8.8
    environment:
      - PYTHONUNBUFFERED=1

```

### Execution Steps

1. **Build the images:**
```bash
docker-compose build

```

2. **Start the Bot (Background):**
```bash
docker-compose up -d bot

```

3. **Run the Controller (Interactive):**
To access the interactive menu and send commands, run:
```bash
docker-compose run controller

```

4. **Shutdown:**
```bash
docker-compose down

```

---
  title: Networking Concepts Parts 1 to 5
  date: 2025-03-19 09:17:00 +/-TTTT
  image:
    path: /assets/img/favicons/image.jpg
    class: "img-right"
  categories: [networks]
  tags: [networks]
---

  
# Welcome to Networking Concepts – The Chill Guide

So, you wanna understand how computers talk to each other? Maybe you just wanna know what the heck an IP address is, or why your WiFi sucks sometimes? Well, you’re in the right place. This blog series is gonna break down networking from the absolute basics to the deepest details, in a way that even your grandma (or your lazy friend who never reads) could get. We’ll cover how data moves across the internet, what makes a network fast or slow, and even how hackers exploit weak setups. No boring textbook talk—just real, useful knowledge you can actually apply. If you use the internet (which, let’s be real, you do), then this is for you. Let’s get into it. 
---

# Content
## 1. Introduction and Setup  
- What is networking, and why does it matter?  
- Installing Python, VS Code, and GNS3 on Windows, macOS, and Linux  
- Understanding the command line (CLI) for networking  
- Verifying your setup and first network commands  

## 2. Networking Overview  
- What is a network?  
- Circuit-switched vs. packet-switched networks  
- Client-server architecture  
- Network programming and sockets   	
- Hands-on: Sending and analyzing packets using Python and GNS3  

## 3. The Sockets API  
- What are sockets, and how do they work?  
- TCP vs. UDP communication  
- Writing a simple Python client and server  
- Understanding ports and network communication  
- Hands-on: Building a basic chat application  

## 4. The Layered Network Model  
- The OSI model vs. the TCP/IP model  
- How data moves through the network stack  
- Encapsulation and decapsulation  
- Hands-on: Inspecting packet headers using Python and Wireshark  
- Simulating data flow in GNS3  

## 5. Project: HTTP Client and Server  
- How the web works (HTTP and HTTPS)  
- Writing an HTTP client in Python  
- Building a simple web server  
- Handling GET and POST requests  
- Hands-on: Testing with a browser and inspecting traffic with BurpSuite  


---

# 1. Introduction and Setup  

## What is Networking, and Why Does It Matter?  

Networking is what allows **computers, phones, servers, and everything else** to communicate. Without networks, devices would be **isolated**, unable to share data or connect to the internet.  

Think about everything that depends on networking:  
- **Messaging** apps like WhatsApp or iMessage  
- **Websites** like Google and YouTube  
- **Online gaming**  
- **Cloud storage** services like Google Drive  
- **Remote work tools** like Zoom  

Even if you just want to **watch YouTube**, **networking is happening** in the background:  
1. Your **device** asks YouTube for a video.  
2. YouTube’s **servers** send back the data.  
3. Your **device downloads and plays it**.  

Networking is everywhere, and understanding it **lets you take control of how devices communicate** instead of just using the internet blindly.  

---

## What You Will Learn in This Guide  

By the time you finish this blog series, you will:  
- **Understand how data moves across a network**  
- **Learn how computers, servers, and websites communicate**  
- **Write your own network programs in Python**  
- **Simulate real-world networking in GNS3**  
- **Use Wireshark to analyze network traffic**  

We’re going to start **from scratch**, so no experience is needed.  

---

## Setting Up Your Environment  

To learn networking **properly**, we need some tools.  

### What We’re Installing  
1. **Python** – Used for writing network scripts and automation.  
2. **VS Code** – A lightweight code editor for Python.  
3. **GNS3** – A network simulator to test real-world networking.  
4. **Wireshark** – A tool to capture and analyze network traffic.  

We will install everything on **Windows, macOS, and Linux** step by step.  

---

## Installing Python  

Python lets us **write code to interact with networks**, build servers, and analyze data.  

### Windows  
1. Go to [python.org](https://www.python.org/downloads/) and download the latest version.  
2. **Check the box** that says **"Add Python to PATH"** before clicking Install.  
3. Open **Command Prompt** (`Win + R`, type `cmd`, hit Enter) and type:  
   ```sh
   python --version
   ```
   If it says `Python 3.x.x`, the installation was successful.  

![image](https://github.com/user-attachments/assets/6db0ac4d-5d37-4db6-8ac9-702637c203ea)


---

### macOS  
1. Open **Terminal** (`Cmd + Space`, type "Terminal", hit Enter).  
2. Run:  
   ```sh
   brew install python3
   ```  
   (If you don’t have Homebrew, install it first:  
   ```sh
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```  
   Then try again.)  
3. Verify the installation:  
   ```sh
   python3 --version
   ```  

![image](https://github.com/user-attachments/assets/10c1a3eb-085d-4754-9956-b74a7966fe34)


---

### Linux (Debian/Ubuntu)  
1. Open **Terminal** (`Ctrl + Alt + T`).  
2. Run:  
   ```sh
   sudo apt update && sudo apt install python3 -y
   ```
3. Verify the installation:  
   ```sh
   python3 --version
   ```  

---

## Installing VS Code  

VS Code is a lightweight code editor that makes writing Python **easier**.  

### Windows / macOS / Linux  
1. Go to [code.visualstudio.com](https://code.visualstudio.com/) and download it.  
2. Install it like any other program.  
3. Open it and make sure it runs.  

---

## Installing GNS3  

GNS3 allows us to **simulate real-world networks** without needing physical hardware.  

### Windows / macOS  
1. Download from [gns3.com](https://www.gns3.com/software/download).  
2. Install it and follow the setup wizard.  

### Linux (Debian/Ubuntu)  
1. Open **Terminal**.  
2. Run:  
   ```sh
   sudo add-apt-repository ppa:gns3/ppa -y
   sudo apt update
   sudo apt install gns3-gui gns3-server -y
   ```

---

## Installing Wireshark  

Wireshark lets us **capture and analyze network traffic**, which is useful for debugging and learning how data moves.  

### Windows / macOS  
1. Download from [wireshark.org](https://www.wireshark.org/download.html).  
2. Install it and follow the setup wizard.  
3. Open Wireshark and select a **network interface** to monitor traffic.  

### Linux (Debian/Ubuntu)  
1. Open **Terminal**.  
2. Run:  
   ```sh
   sudo apt update && sudo apt install wireshark -y
   ```
3. Allow Wireshark to capture packets without root privileges:  
   ```sh
   sudo usermod -aG wireshark $(whoami)
   ```

**Screenshot Here:** Show Wireshark’s interface with a network interface selected.  

---

## Understanding the Command Line (CLI)  

The **command line** is essential for networking. It lets us:  
- **Check network configurations**  
- **Ping and trace network paths**  
- **Run Python scripts efficiently**  

---

### Basic CLI Commands  

#### Windows (Command Prompt)  
```sh
ipconfig  # Shows network configuration
ping google.com  # Sends packets to Google to check connectivity
```

#### Linux/macOS (Terminal)  
```sh
ip a  # Shows network interfaces and IP addresses
ping google.com  # Sends packets to Google to check connectivity
```

---

## Hands-On: Verifying Your Setup  

### 1. Check if Python is Installed  
Run:  
```sh
python --version  # Windows
python3 --version  # macOS/Linux
```

### 2. Test Your Connection to the Internet  
Run:  
```sh
ping google.com
```

If you get **replies**, your network is working.  

---

## Recap  

By now, you should have:  
- Installed **Python** for network programming  
- Installed **VS Code** for writing and testing code  
- Installed **GNS3** for simulating real networks  
- Installed **Wireshark** to capture network traffic  
- Learned some **basic CLI commands**  

Everything is **set up and ready**.  

---

# 2. Networking Overview  

## What is a Network?  

A **network** is simply **two or more devices that communicate** with each other.  

This could be:  
- **Two computers connected with a cable**.  
- **Your phone and WiFi router**.  
- **Millions of servers powering the internet**.  

### Why Do We Need Networks?  
Without networks, every device would be **isolated**. You couldn’t:  
- Access the internet.  
- Use cloud services.  
- Send emails.  
- Play online games.  

Networking enables **data to flow between devices**, whether they're in the **same room** or on **opposite sides of the world**.  

### How Data Moves in a Network  
When two devices communicate, they **send and receive data** in a structured way.  
1. The **sender** breaks data into **packets**.  
2. Each packet **travels across the network**.  
3. The **receiver** reassembles the packets.  

This happens in **fractions of a second**, whether you're:  
- **Streaming a video.**  
- **Downloading a file.**  
- **Sending a message.**  

---

## Circuit-Switched vs. Packet-Switched Networks  

### Circuit-Switched Networks (Old Telephone System)  
Before the internet, we used **circuit-switched networks**, like landline phones.  

- When you made a call, a **dedicated path** was reserved **just for you**.  
- That connection **stayed open the entire call**, even if you were silent.  
- Once the call ended, the line was **freed up** for someone else.  

#### Problems with Circuit Switching  
- **Inefficient** – Wastes bandwidth when there is silence.  
- **Limited Connections** – Only a certain number of people can talk at the same time.  

---

### Packet-Switched Networks (How the Internet Works)  
The **internet does not reserve** a full line for every conversation. Instead, it:  
- **Breaks data into small packets**.  
- **Sends packets individually** to their destination.  
- **Reassembles them at the receiving end**.  

This makes networking **more efficient**, **faster**, and **scalable**.  

---

## Hands-On: Seeing Packets in Action  

### Step 1: Checking Your Own IP Address  

#### Windows (Command Prompt)  
```sh
ipconfig
```

#### Linux/macOS (Terminal)  
```sh
ip a
```

This shows your **local IP address**, which your router assigns to your device.  

---

### Step 2: Testing Network Connectivity  

#### Windows (Command Prompt)  
```sh
ping google.com
```

#### Linux/macOS (Terminal)  
```sh
ping google.com
```

If you get replies, your network is working.  

---

### Step 3: Capturing Packets with Wireshark  

1. **Open Wireshark**.  
2. Select your **network interface** (WiFi or Ethernet).  
3. Click **Start Capture**.  
4. In a terminal or Command Prompt, run:  
   ```sh
   ping google.com
   ```
5. **Stop the capture** after a few seconds.  
6. Look for **ICMP packets** (used by `ping`).  

---

### Step 4: Sending Packets with Python  

Python allows us to **send network packets** using sockets.  

#### Install Required Libraries  
```sh
pip install scapy requests
```

#### Python Script to Send Packets  
```python
from scapy.all import *
import time

destination_ip = "8.8.8.8"  # Google's public DNS server

for i in range(5):
    packet = IP(dst=destination_ip)/ICMP()
    send(packet)
    print(f"Packet {i+1} sent to {destination_ip}")
    time.sleep(1)
```

### What This Does  
- Creates an **ICMP packet** (same as `ping`).  
- Sends it to `8.8.8.8` (Google’s DNS).  
- Prints a message after each packet is sent.  

#### Run the Script  
```sh
python packet_sender.py
```

### Check the Packets in Wireshark  
1. Open **Wireshark**.  
2. Start a **capture** on your network interface.  
3. Run the script again.  
4. You should see **ICMP packets going to 8.8.8.8**.  

---

# 3. The Sockets API  

## What is the Sockets API?  

A **socket** is a fundamental building block of networking.  
It allows two devices to **communicate with each other over a network**.  

Think of a socket as a **direct communication line** between two programs, just like a phone call between two people.  
- You **dial a number** (connect to an IP and port).  
- You **say something** (send data).  
- The other person **listens and responds** (receives and processes data).  
- Once the conversation is over, you **hang up** (close the connection).  

The **Sockets API** is a set of functions that allow programmers to:  
- **Create network connections** between devices.  
- **Send and receive data** over the internet.  
- **Build custom network applications** like chat apps, web servers, and game clients.  

Every time you open a website, send a message, or stream a video, **sockets are working in the background**.  

---

## How Do Computers Communicate Over a Network?  

For two computers to **exchange data**, they need:  

1. **An IP Address** – A unique address for each device on the network (like a house address).  
2. **A Port Number** – A specific communication channel inside the computer (like an apartment number).  

When a program **opens a socket**, it uses an **IP address** and a **port number** to communicate with another device.  

---

## What is a Port?  

A **port** is like an apartment number in a building.  
- A building (IP address) can have **many apartments (ports)**.  
- Each port handles a **specific type of communication**.  

For example:  
- **Port 80** – Used for websites (HTTP).  
- **Port 443** – Used for secure websites (HTTPS).  
- **Port 22** – Used for remote login (SSH).  
- **Port 53** – Used for converting domain names into IP addresses (DNS).  

Each program that needs network access **listens on a specific port**.  

---

## Hands-On: Checking Open Ports  

To see which ports are currently active on your computer:  

### Windows (Command Prompt)  
```sh
netstat -ano
```

### Linux/macOS (Terminal)  
```sh
netstat -tulnp
```

This command lists all **open ports** and the programs using them.  

---

## TCP vs. UDP: Two Ways to Communicate  

### What is TCP?  
**TCP (Transmission Control Protocol)** ensures reliable communication.  
- **All packets arrive in order**.  
- **Lost packets are resent**.  
- **Data delivery is guaranteed**.  
- **Slower** but more reliable.  

TCP is used for:  
- **Web browsing** (HTTP, HTTPS).  
- **File transfers** (FTP, SFTP).  
- **Email** (SMTP, IMAP, POP3).  

### What is UDP?  
**UDP (User Datagram Protocol)** is faster but less reliable.  
- **Packets might arrive out of order**.  
- **Packets might be lost and not resent**.  
- **Data delivery is not guaranteed**.  
- **Faster** but less reliable.  

UDP is used for:  
- **Online gaming** (small delays don’t matter).  
- **Live video streaming** (speed is more important than perfect accuracy).  
- **VoIP calls** (real-time communication).  

---

## Hands-On: Writing a Basic TCP Client  

### Step 1: Create a Simple TCP Client  

This **client** will connect to a **server** and send a message.  

#### Create a file called `tcp_client.py`:  
```python
import socket

# Define server IP and port
server_ip = "127.0.0.1"  # Localhost (your own machine)
server_port = 12345       # Any unused port

# Create a TCP socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client.connect((server_ip, server_port))
print(f"Connected to {server_ip}:{server_port}")

# Send a message
message = "Hello, Server!"
client.send(message.encode())

# Receive response
response = client.recv(1024).decode()
print(f"Received from server: {response}")

# Close the connection
client.close()
```

---

### Step 2: Create a TCP Server  

This **server** will listen for incoming connections from a client.  

#### Create a file called `tcp_server.py`:  
```python
import socket

# Define IP and port to listen on
server_ip = "127.0.0.1"  # Localhost
server_port = 12345

# Create a TCP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind to the IP and port
server.bind((server_ip, server_port))

# Listen for incoming connections (max 5 clients in queue)
server.listen(5)
print(f"Server listening on {server_ip}:{server_port}")

while True:
    # Accept a connection
    client_socket, client_address = server.accept()
    print(f"Accepted connection from {client_address}")

    # Receive data from the client
    data = client_socket.recv(1024).decode()
    print(f"Received: {data}")

    # Send a response
    response = "Message received"
    client_socket.send(response.encode())

    # Close the connection
    client_socket.close()
```

---

### Step 3: Run the Server and Client  

#### First, Start the Server  
```sh
python tcp_server.py
```

#### Then, In a New Terminal, Start the Client  
```sh
python tcp_client.py
```

**Expected Output (Server Side):**  
```
Server listening on 127.0.0.1:12345
Accepted connection from ('127.0.0.1', 54321)
Received: Hello, Server!
```

**Expected Output (Client Side):**  
```
Connected to 127.0.0.1:12345
Received from server: Message received
```

---

## Hands-On: Capturing TCP Packets in Wireshark  

1. Open **Wireshark**.  
2. Start a **capture** on your network interface.  
3. Run the **TCP server and client** again.  
4. In Wireshark, **filter packets by port number**:  
   ```
   tcp.port == 12345
   ```
5. You should see **packets exchanged between the client and server**.  

---




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


# Before We Begin: Setting Up Like a Pro

## Do You Even Need to Install This?

You could just read this blog and move on, but if you actually want to **see networking in action**, you’ll need to install some tools. We’re not just talking about theory here—you’ll be **writing Python scripts, simulating real networks, and troubleshooting like a pro**.  

If you follow along, you’ll understand **how data moves, how the internet works, and how to automate networking with code.** This isn’t just for learning, it’s **preparing you for real-world skills**.

---

# 1. Installing Python

### Why Do We Need Python?
- Because networking isn’t just cables and routers, it’s about **programming, automation, and security.**
- We’ll use Python to **analyze packets, build network tools, and simulate attacks (ethically, of course).**
- Most networking tools today **are written in Python**, so knowing it is essential.

---

## Windows
1. Go to [python.org](https://www.python.org/downloads/) and download the latest version.
2. **IMPORTANT:** Check the box **"Add Python to PATH"** before clicking Install.
3. Open Command Prompt (`Win + R`, type `cmd`, hit Enter) and verify the installation:
   ```sh
   python --version
   ```
   If it shows `Python 3.x.x`, you’re good.

---

## macOS
1. Open Terminal (`Cmd + Space`, type "Terminal", hit Enter).
2. Run:
   ```sh
   brew install python3
   ```
   If you don’t have Homebrew, install it first:
   ```sh
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
   Then try again.
3. Verify the installation:
   ```sh
   python3 --version
   ```

---

## Linux (Debian/Ubuntu)
1. Open Terminal (`Ctrl + Alt + T`).
2. Run:
   ```sh
   sudo apt update && sudo apt install python3 -y
   ```
3. Verify:
   ```sh
   python3 --version
   ```

---

## Arch Linux
1. Open Terminal.
2. Run:
   ```sh
   sudo pacman -S python
   ```
3. Verify:
   ```sh
   python --version
   ```

---

# 2. Installing VS Code

We need a **good code editor**, and VS Code is lightweight, cross-platform, and great for Python.

### Windows / macOS / Linux
1. Go to [code.visualstudio.com](https://code.visualstudio.com/) and download it.
2. Install it like any other program.
3. Open it and make sure it runs.

### Adding VS Code to Command Line (Optional but Useful)
- **Windows**: Open VS Code, press `Ctrl+Shift+P`, search for `"Shell Command: Install"` and select it.
- **macOS**:  
  ```sh
  sudo ln -s "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" /usr/local/bin/code
  ```
- **Linux** (if not already installed):  
  ```sh
  sudo apt install code -y  # Ubuntu/Debian
  sudo pacman -S code       # Arch
  ```

---

# 3. Installing GNS3 (For Network Simulation)

We’ll use **GNS3** to **simulate real networks**, from small LANs to **full-scale internet routing setups**.

### Windows / macOS
1. Download from [gns3.com](https://www.gns3.com/software/download).
2. Install it and follow the setup wizard.

### Linux (Debian/Ubuntu)
1. Open Terminal.
2. Run:
   ```sh
   sudo add-apt-repository ppa:gns3/ppa -y
   sudo apt update
   sudo apt install gns3-gui gns3-server -y
   ```

### Arch Linux
1. Open Terminal.
2. Run:
   ```sh
   sudo pacman -S gns3-gui gns3-server
   ```

---

# 4. Understanding the Command Line (CLI)

You **can’t** work with networking without using the **command line**, so let’s get comfortable with it.  
This is **not optional**—you’ll be using it for **configuring networks, troubleshooting issues, and running scripts**.

---

## Windows (Command Prompt & PowerShell)
- Open Command Prompt (`Win + R`, type `cmd`, hit Enter).
- **Navigating Folders**:
  ```sh
  cd path\to\folder
  ```
- **List files**:
  ```sh
  dir
  ```
- **Check your IP Address**:
  ```sh
  ipconfig
  ```
- **Test network connectivity (Ping Google)**:
  ```sh
  ping google.com
  ```

---

## macOS/Linux (Terminal)
- Open Terminal.
- **Navigating Folders**:
  ```sh
  cd path/to/folder
  ```
- **List files**:
  ```sh
  ls -l
  ```
- **Check your IP Address**:
  ```sh
  ip a  # Linux
  ifconfig  # macOS (May require: sudo ifconfig)
  ```
- **Test network connectivity (Ping Google)**:
  ```sh
  ping google.com
  ```
- **Trace the path of your internet request (see all routers your data passes through)**:
  ```sh
  traceroute google.com  # Linux/macOS
  tracert google.com     # Windows
  ```

---

# 5. Running Python from the CLI

Once you have Python installed, you’ll want to run your scripts from the command line.

### Windows:
```sh
python script.py
```

### macOS/Linux:
```sh
python3 script.py
```

If you see an error like **"command not found"**, try `python` instead of `python3`.

---

# 6. Final Check

Make sure everything works:

- Open **VS Code** and make sure it runs.
- Open **Terminal/Command Prompt** and type:
  ```sh
  python --version
  ```
  It should return **Python 3.x.x**.
- Open **GNS3** and start a blank project.
- Run:
  ```sh
  ping google.com
  ```
  If you get responses, your internet is working fine.

---

# You’re Ready

Now that everything’s set up, you’re ready to **start learning networking the right way**.  
No theory without practice. **Let’s get to it.**

---


# Networking Overview – How Computers Talk to Each Other  

Imagine a world without networking.  

- No internet.  
- No texting.  
- No online games.  
- No streaming.  

Your phone would be a **fancy calculator**. Your laptop? A **glorified notepad**.  

So how do computers **talk to each other**? That’s what networking is all about.  

Before we jump into **IP addresses, packets, or protocols**, let’s start with **the absolute basics**.

---

# 1️⃣ What is a Network?  

A **network** is just a group of **devices** that can talk to each other.  

It could be:  
- **Two computers connected** with a cable.  
- **Your phone and your WiFi router.**  
- **Millions of servers** powering the internet.  

If two or more devices **share information**, **that's networking.**  

---

# 2️⃣ Circuit-Switched vs. Packet-Switched Networks  

## 🛜 Circuit-Switched Networks (Old-School Phone Calls)  
Before the internet, we used **circuit-switched networks**, like **landline phones**.  

- When you made a call, the phone company **reserved a dedicated path** just for you.  
- The line stayed open, **even if you weren’t talking**.  
- Once you hung up, the circuit was **freed for someone else**.  

### 🔴 Why is this bad?  
- **Inefficient** → If you weren’t talking, the line was still **wasting resources**.  
- **Expensive** → Reserved connections meant fewer calls could happen at the same time.  

---

## 🌐 Packet-Switched Networks (How the Internet Works)  
The internet doesn’t **reserve a full connection** for every conversation.  
Instead, it **breaks data into small pieces called packets** and sends them **individually**.  

- Each packet **finds the fastest path** to the destination.  
- The receiver **reassembles the packets** into the original message.  

### 🟢 Why is this better?  
- **More efficient** → Multiple people can use the same network at once.  
- **More reliable** → If one path is slow, packets take **another route**.  
- **Scalable** → It allows billions of devices to communicate at the same time.  

---

## 3️⃣ Hands-On: See Packets in Action  

You’re about to **see packets traveling** in real-time.  

### 🔹 Windows (Command Prompt)  
1. Open **Command Prompt** (`Win + R`, type `cmd`, hit Enter).  
2. Type:  
   ```sh
   ping google.com
   ```
3. You’ll see something like this:  

   ```
   Pinging google.com [142.250.187.206] with 32 bytes of data:
   Reply from 142.250.187.206: bytes=32 time=20ms TTL=114
   Reply from 142.250.187.206: bytes=32 time=18ms TTL=114
   ```

This means your computer **sent packets to Google**, and Google’s server **responded**.

---

### 🔹 Linux/macOS (Terminal)  
1. Open **Terminal**.  
2. Type:  
   ```sh
   ping google.com
   ```
3. You’ll see similar output, showing **how long each packet takes to travel**.  

---

# 4️⃣ Client-Server Architecture – Who Talks to Who?  

Every time you visit a website, you're using a **Client-Server Model**.  

- **Client** → The device **requesting** something (your phone, laptop, browser).  
- **Server** → The device **responding** (Google’s web server, a database, a game server).  

---

## 🌎 Example: Visiting a Website  
When you type `google.com` in your browser:  
1. Your **computer (client)** sends a request → **"Give me Google's homepage!"**  
2. Google’s **server** responds → **"Here’s the page!"**  
3. Your browser **renders it**, and you see the website.  

### 🔹 Hands-On: Checking a Website’s Server  

Want to see **where Google’s servers are located**?  

#### 🖥 Windows (Command Prompt):  
```sh
nslookup google.com
```

#### 🖥 Linux/macOS (Terminal):  
```sh
dig google.com +short
```

It will return **Google’s IP address**, proving that your computer talks to a **real server**.

---

# 5️⃣ The OS, Network Programming, and Sockets  

Your **Operating System (OS)** controls how your computer talks to a network.  
- **Windows, macOS, Linux** → Each handles networking **slightly differently**.  
- **Networking Programming** → We use programming languages (like Python) to **send, receive, and analyze network data**.  

---

## 🖧 What are Sockets?  
A **socket** is like a **phone line** for computers.  
- It lets two devices **send and receive data**.  
- Every website, game, and messaging app **uses sockets** under the hood.  

---

## 6️⃣ Hands-On: Get Your Own IP Address  

### 🔹 Windows (Command Prompt):  
```sh
ipconfig
```

### 🔹 Linux/macOS (Terminal):  
```sh
ip a
```

This will show your **local IP address**, which your router gives you.  

---

# 7️⃣ Protocols – The Rules of the Internet  

A **protocol** is just an **agreed way of communicating**.  
It’s like a language – if two devices don’t follow the same rules, they can’t talk.  

Some of the most important network protocols are:  

| Protocol | What It Does |
|----------|-------------|
| **TCP**  | Reliable communication, ensures all packets arrive. |
| **UDP**  | Faster, but doesn’t check if packets are lost. |
| **HTTP** | How websites send and receive data. |
| **HTTPS** | Secure version of HTTP, encrypts data. |
| **IP**   | Addresses every device on the internet. |
| **DNS**  | Converts domain names (like google.com) into IP addresses. |

---

# 8️⃣ Wired vs. Wireless – How Data Moves  

### 📡 Wired Networks (Ethernet)  
- Faster  
- More stable  
- No interference  

### 🌍 Wireless Networks (WiFi)  
- More convenient  
- Slower than Ethernet  
- Can be affected by walls and interference  

---

# 9️⃣ Hands-On: Using Python for Network Commands  

### 🔹 Check Your Public IP Address  
Want to know the **IP address websites see** when you visit them?  

#### 🖥 Terminal (Linux/macOS) / Command Prompt (Windows):  
```sh
curl ifconfig.me
```

#### 🖥 Python Script:  
```python
import requests
ip = requests.get("https://ifconfig.me").text
print(f"Your public IP: {ip}")
```

---

# 🔟 Recap – What You Just Learned  

✅ How networks work and why they matter  
✅ Circuit vs. packet switching  
✅ How clients and servers communicate  
✅ What sockets are and why we need them  
✅ The key network protocols  
✅ Wired vs. wireless networks  
✅ Hands-on practice with commands, Python, and GNS3  

You’re now ready to **go deeper into real networking concepts.**  
Next up: **The Sockets API.**


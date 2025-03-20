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
  
  # Introduction
  
  Networking is the reason you can send memes, watch YouTube, or argue with strangers online. It’s how computers talk to each other, whether they’re in the same room or across the planet. But how does this actually work?  
  
  In this section, we’ll break it down step by step, from **the big picture** to **the smallest technical details**, so even if you’ve never touched a network setting in your life, you’ll get it.  
  
  ---
  
  ## The Big Idea of Networking  
  
  At its core, networking is **just moving data from one place to another**. Sounds simple, right? Well, here’s the problem:  
  
  - How does your computer **find** where to send the data?  
  - How does it make sure the data **gets there safely**?  
  - How does it **choose the best path** to take?  
  
  ### Think of a Package Delivery System  
  
  Imagine you need to **send a package** to a friend in another country. Here’s what happens:  
  
  1. **You write their address** on the box.  
  2. **A delivery truck picks it up.**  
  3. **The package moves through multiple hubs.**  
  4. **It eventually arrives at the destination.**  
  
  That’s basically **how the internet works**—except instead of trucks and boxes, we have **routers and data packets**.  
  
  - **Data packets** = Packages  
  - **IP addresses** = Destination addresses  
  - **Routers** = Post offices that decide where the package goes next  
  
  Without networking, your device would be **a lonely island**, unable to communicate with anyone.  
  
  ---
  
  ## Identifying Source and Destination Computers  
  
  If we want data to travel across a network, we need to know **where it’s coming from** and **where it’s going**. This is where **IP addresses** come in.  
  
  🔹 **IP Address = A Computer’s Home Address**  
  
  Every device on a network—your phone, laptop, router—has an IP address. When you send data, your device **adds its own IP address (source)** and the **destination IP address** so the network knows where to send it.  
  
  ### Checking Your Own IP Address  
  
  You can find your **local IP address** (inside your home network) by running:  
  
  ```sh
  ip a  # On Linux/macOS
  ipconfig  # On Windows
  ```
  
  You’ll see something like this:  
  
  ```sh
  3: wlan0: <UP,BROADCAST,RUNNING,MULTICAST> mtu 1500
      inet 192.168.1.24/24 brd 192.168.1.255 scope global wlan0
  ```
  
  Here, **192.168.1.24** is your private IP address. Your **router assigns this to your device** inside your home network.  
  
  To check your **public IP address** (the one websites see when you visit them), run:  
  
  ```sh
  curl ifconfig.me
  ```
  
  You’ll get something like:  
  
  ```sh
  203.0.113.42
  ```
  
  This is the **public IP assigned to you by your ISP (Internet Service Provider)**.  
  
  ---
  
  ### How Does Your Computer Find Other Devices?  
  
  When you visit **google.com**, your computer **doesn’t understand domain names**. It needs to find Google’s **IP address** before it can send any data.  
  
  To see this in action, run:  
  
  ```sh
  nslookup google.com  # Windows
  dig google.com +short  # Linux/macOS
  ```
  
  You’ll get something like:  
  
  ```sh
  142.250.185.78
  ```
  
  Now your computer knows that **google.com = 142.250.185.78**, and it can send your request.  
  
  ---
  
  ### What Happens When You Send Data?  
  
  1. **You enter a website URL.**  
  2. **Your computer looks up the IP address.**  
  3. **Your request is sent to the destination IP.**  
  4. **Data travels through multiple routers.**  
  5. **The website responds, and you see the page.**  
  
  ---
  
  ### Seeing It in Action  
  
  Want to see **how your request travels across the internet**? Run:  
  
  ```sh
  traceroute google.com   # On Linux/macOS
  tracert google.com      # On Windows
  ```
  
  You’ll get something like this:  
  
  ```sh
  1  192.168.1.1 (192.168.1.1)  2.372 ms
  2  10.24.12.1 (10.24.12.1)  10.485 ms
  3  203.0.113.5 (203.0.113.5)  20.678 ms
  4  142.250.185.78 (Google)  40.142 ms
  ```
  
  Each **hop** is a router forwarding your request closer to the destination.  
  
  ---
  
  ## Ensuring Data Integrity  
  
  Okay, so we now **know where data is going**. But how do we make sure it **doesn’t get corrupted** or **lost** along the way?  
  
  🔹 **Imagine sending a text message, but your friend receives gibberish.** That’s what happens when **data gets corrupted**.  
  
  ### How Networks Keep Data Safe:  
  1. **Breaking Data into Packets** – Instead of sending one huge file, networks **split it into chunks**.  
  2. **Adding a Checksum** – Each packet gets a **security seal** (checksum) to verify that nothing got messed up.  
  3. **Acknowledging Receipt** – The receiver sends a “**Got it!**” message for every packet.  
  4. **Resending Lost Packets** – If something is missing, the sender **resends it automatically**.  
  
  ### Seeing It in Action  
  
  Want to **see network packets in real-time**? Run:  
  
  ```sh
  sudo tcpdump -i wlan0
  ```
  
  This will **capture all the network traffic** on your device. You’ll see **raw packets** moving through your network, proving that **your data really does travel in chunks**.  
  
  ---
  
  ## Routing Data Across Networks  
  
  We know that computers **communicate using IP addresses**, but how does data actually move from one computer to another? It doesn’t just teleport. Instead, it **jumps between multiple routers** until it reaches its final destination.  
  
  This is called **packet switching**, and it’s the core idea behind modern networking.  
  
  ---
  
  ## How Data Travels: The Packet Journey  
  
  Every time you send data, it **doesn’t travel in one big chunk**. Instead, it’s broken into **packets**—small, structured pieces of information. Each packet contains:  
  
  - **The source IP address** (where it came from).  
  - **The destination IP address** (where it’s going).  
  - **A sequence number** (so packets can be reassembled in order).  
  - **The actual data** (a small piece of the full message).  
  
  Think of sending a large book **one page at a time** through the mail. Each envelope contains:  
  
  1. **The sender's address** (your house).  
  2. **The receiver's address** (your friend’s house).  
  3. **A page number** (so your friend knows the order).  
  4. **One page of the book** (the actual data).  
  
  Your friend gets **many envelopes**, but once they **put the pages back in order**, they have the full book. That’s exactly how packet switching works.  
  
  ---
  
  ## The Role of Routers: The Post Offices of the Internet  
  
  Routers are devices that **move data between networks**. Their job is to **receive packets and forward them to the next stop** until they reach the destination.  
  
  Every router has a **routing table**, a set of rules that help it decide:  
  
  - **Where to send a packet next.**  
  - **Which path is the fastest or most efficient.**  
  - **How to handle network congestion.**  
  
  To see your router’s routing table, run:  
  
  ```sh
  ip route show  # On Linux/macOS
  route print    # On Windows
  ```
  
  Example output:  
  
  ```sh
  default via 192.168.1.1 dev wlan0
  192.168.1.0/24 dev wlan0 proto kernel scope link
  ```
  
  This means:  
  
  - **"default via 192.168.1.1"** → Any unknown IP address is sent to **192.168.1.1** (your router).  
  - **"192.168.1.0/24 dev wlan0"** → Devices in **192.168.1.x** are inside your local network.  
  
  Your home router is **the first stop** for all your internet traffic. It receives your request and forwards it to your ISP’s network. From there, your data moves through a series of routers until it reaches the destination.  
  
  ---
  
  ## How a Router Decides Where to Send Data  
  
  Routers don’t randomly guess where to send packets. They use **two main strategies**:  
  
  1. **Static Routing** – A router has a **fixed list of destinations** and knows exactly where to send packets. This is used in small, private networks.  
  2. **Dynamic Routing** – Routers **learn** the best paths **automatically** using special protocols. This is how the internet routes billions of packets every second.  
  
  To check if your system is using static or dynamic routing, run:  
  
  ```sh
  netstat -r  # On Linux/macOS
  netstat -rn # On Windows
  ```
  
  Example output:  
  
  ```sh
  Kernel IP routing table
  Destination  Gateway        Genmask        Flags  Iface
  0.0.0.0      192.168.1.1    0.0.0.0        UG     wlan0
  192.168.1.0  0.0.0.0        255.255.255.0  U      wlan0
  ```
  
  The **UG** flag means **this is a gateway route**—data is sent outside your network when it doesn’t match any known local addresses.  
  
  ---
  
  ## Seeing Packet Routing in Action  
  
  To see **how your data travels across the internet**, use:  
  
  ```sh
  traceroute google.com   # On Linux/macOS
  tracert google.com      # On Windows
  ```
  
  Example output:  
  
  ```sh
  1  192.168.1.1 (192.168.1.1)  2.372 ms
  2  10.24.12.1 (10.24.12.1)  10.485 ms
  3  203.0.113.5 (203.0.113.5)  20.678 ms
  4  142.250.185.78 (Google)  40.142 ms
  ```
  
  Each line represents a **router** that your request passed through. The numbers on the right show the **latency in milliseconds**, or how long it took for the packet to reach that router and return.  
  
  ---
  
  ## What Happens When a Route is Broken?  
  
  Sometimes, routers **fail** or **become overloaded**. When that happens, data packets:  
  
  1. **Take an alternate path** if possible.  
  2. **Get dropped** if no path is available.  
  
  To check for packet loss, run:  
  
  ```sh
  ping -c 10 google.com  # On Linux/macOS
  ping -n 10 google.com  # On Windows
  ```
  
  If some packets don’t come back, the network **is dropping traffic**.  
  
  ---
  
  ## Hardware and Software Support  
  
  Networking isn’t just **software**—it also depends on **hardware** to function correctly.  
  
  ### Network Hardware  
  
  1. **Routers** – Direct data between networks.  
  2. **Switches** – Handle communication **inside** a network.  
  3. **Modems** – Connect homes and businesses to ISPs.  
  4. **Network Interface Cards (NICs)** – Enable computers to send and receive data.  
  5. **Cables & Wireless Signals** – The actual medium that carries data.  
  
  To check your system’s **network hardware**, run:  
  
  ```sh
  lspci | grep -i network  # On Linux/macOS
  wmic nic get Name        # On Windows
  ```
  
  This will show details about your **network interface card (NIC)**, which connects you to the network.  
  
  ---
  
  ### Network Software  
  
  Networking also relies on **software components** to manage data transfer.  
  
  1. **Operating Systems** – Windows, Linux, and macOS handle **network connections**.  
  2. **Networking Protocols** – TCP, IP, and UDP define how data moves.  
  3. **Applications** – Web browsers, messaging apps, and cloud services all rely on networking.  
  
  To see **active network connections** on your machine, run:  
  
  ```sh
  netstat -tulnp  # On Linux/macOS
  netstat -ano    # On Windows
  ```
  
  Example output:  
  
  ```sh
  Proto Recv-Q Send-Q Local Address   Foreign Address State   PID/Program name
  tcp   0      0     192.168.1.24:22  203.0.113.50:54321 ESTABLISHED 1342/sshd
  ```
  
  This means:  
  - Your computer (**192.168.1.24**) has an **SSH connection** to **203.0.113.50**.  
  - The connection is **established**, meaning data is actively being sent.  
  
  ---
  
  

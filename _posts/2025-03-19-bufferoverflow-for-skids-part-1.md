---
title: BufferOverflow for Skids - Part I
date: 2025-03-19 14:54:00 +/-TTTT
image:
  path: /assets/posts/bof-part1/draw.png
  class: "img-right"
categories: [CyberSecurity]
tags: [lowlevelprogramming, bof, securecoding]  
---


Alright, so you’re still stuck on this ridiculously basic buffer overflow stuff? Fine. Let’s do this one more time, and try to keep up.

A **buffer** is just a tiny storage box in your computer’s brain that holds some temporary data. Now, a **buffer overflow** happens when some psychopath tries to stuff way too much data into that box, and it spills out everywhere. Think of pouring a gallon of soda into a shot glass. What happens? It overflows and makes a mess. And where does this mess land? On important parts of memory that tell your computer what to do next.

One key piece it can mess up is the **return address** basically, a sticky note on the computer’s to-do list that says, “Hey, after you finish this task, go here next.” This note lives on the **stack**, which is just a set of instructions stacked on top of each other. Overflow that buffer, and boom you knock the stack over, scratch all over those sticky notes, and suddenly the computer is taking orders from you instead. Badass, right?

Now, to actually hijack a program, you need to know exactly how much extra garbage data (or ‘padding’) you need to reach that return address. This is called finding the **offset**. The usual way? Just keep throwing junk at the program until it crashes and tells you exactly where things went wrong.

Now, let’s talk about the heap. **Heap** is a big, messy storage room where your computer keeps track of dynamic memory stuff that can grow and shrink as needed. When you ask for memory, the heap gives you a chunk, but if you’re not careful and you overflow a buffer here, you can overwrite other important data stored in the heap.

And just like the stack, the heap has its own set of rules and structures. If you mess with the heap, you can corrupt pointers those little arrows that tell the computer where to find things. If you change a pointer’s direction, you could make it point to a place it shouldn’t, leading to all sorts of chaos.

But wait, modern computers have some security tricks up their sleeves, like **NX** (No-Execute) and **DEP** (Data Execution Prevention). These try to stop your plans by blocking certain areas of memory from running code. Annoying, but not unbeatable. 

Enter **Return-to-Libc (R2L)** attack;

<img src="https://c.tenor.com/ScO52e_roDgAAAAd/tenor.gif" alt="GIF" width="200" />

Instead of injecting new code, you just hijack existing functions the program already trusts. By hijacking these trusted functions, we can execute arbitrary commands without the need for injecting new code. This method is particularly effective because it often bypasses security mechanisms designed to detect and block code injection, as the program is simply executing its own trusted functions. Since these functions are already part of the program's environment, they are less likely to raise suspicion. So we can leverage this trust to perform malicious actions, such as spawning a shell or manipulating data, all while appearing to operate within the normal limits of the program's functionality.

And because nothing in computer science is ever simple, we have **endianness** a fancy word for “sometimes computers store numbers backward for no good reason.” So when you’re writing an exploit, you might have to flip memory addresses like a dyslexic hacker just to get them to work. (More to cover in Part II)

Alright, enough talk; time for some action. Here’s some code that even your dog could understand.

### The “Safe” Version:

```c
#include <stdio.h>
#include <string.h>
#include <unistd.h>

void secure() {
    char buffer[200];
    read(0, buffer, 200); // safe. no stupid mistakes here
    printf("you entered: %s\n", buffer);
    printf("L=length: %lu\n", strlen(buffer));
}

int main() {
    secure();
    return 0;
}
```
{: file='/home/elliot/labs/safe.c'}

- Let's run this code for the fcuk sake :

```shell
elliot@matrix:~/lab$ gcc safe.c -o safe 
elliot@matrix:~/lab$ printf 'A%.0s' {1..400} | ./safe 
you entered: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAApo
L=length: 206
```

Nothing exciting. No explosions, No Nuclear bombs dropping from the sky. Just a normal, well-behaved program. Now, let’s get reckless.


### The “Oops, I Broke the Computer” Version:

```c
#include <stdio.h>
#include <string.h>
#include <unistd.h> 

// disable specific warnings for demonstration purposes
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wstringop-overflow"

void insecure() {
    char buffer[200];
    (void)read(0, buffer, 400); // that’s 200 bytes too many!
    printf("you entered: %s\n", buffer);
    printf("length: %lu\n", strlen(buffer));
}

#pragma GCC diagnostic pop

int main() {
    insecure();
    return 0;
}

```
{: file='/home/elliot/oops-break-bed-not-computers.c'}

- Let's run this code :

```shell
elliot@matrix:~/lab$ gcc oops-break-bed-not-computers.c -o oops
elliot@matrix:~/lab$ printf 'A%.0s' {1..400} | ./oops 
you entered: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA�^;�U
length: 406
Segmentation fault (core dumped)
```

Here, we’re trying to stuff **400 bytes** into a space meant for **200**. The extra junk spills over and starts stepping on important memory. Next thing you know, your program is running wherever you tell it to. That’s how buffer overflow exploits are born.

### The “Let’s Ruin This Program on Purpose” Version:

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h> 

// disable specific warnings on modern compilers for demonstration purposes
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wstringop-overflow"

void hackme() {
    system("ls > hacked.txt");
}

int main() {
    char buffer[200];
    read(0, buffer, 250); // guess what? another overflow
    printf("you entered: %s\n", buffer);
    
    
    return 0; 
}

#pragma GCC diagnostic pop

```
{: file="/home/elliot/ruin-and-get-rce.c"}
- Let's run this code:

```shell
elliot@matrix:~/lab$ gcc ruin-and-get-rce.c -o ruin-get-rce 
elliot@matrix:~/lab$ printf 'A%.0s' {1..400} | ./ruin-get-rce 
you entered: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
Segmentation fault (core dumped)
```
> In this code, `hackme()` is never actually called… unless you overflow the buffer and overwrite the return address to point straight at it. Now, instead of doing what it’s supposed to, the program jumps to `hackme()` and runs `system("ls > hacked.txt")`, creating a file with a list of everything in the directory. Again, More to cover in Part II
{: .prompt-info }

### The “This is Just Asking for Trouble” Code:

```c
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
    char buffer[500];
    strcpy(buffer, argv[1]); // no safety checks instant disaster
    return 0;
}
```
{: file="/home/elliot/labs/trouble.c"}

Output:
```shell
elliot@matrix:~/lab$ gcc trouble.c -o trouble
elliot@matrix:~/lab$ printf 'A%.0s' {1..100} | ./trouble 
Segmentation fault (core dumped)
elliot@matrix:~/lab$ printf 'A%.0s' {1..501} | ./trouble 
Segmentation fault (core dumped)
```

This beauty doesn’t even pretend to be safe. It takes whatever input you throw at it, no matter how long, and blindly copies it into `buffer`. If you give it more than **500 characters**, it will happily overwrite important memory, including the return address. And just like that, you control where the program jumps next.

So there you have it. Overflowing buffers is like tricking a GPS into driving you straight to your own house instead of its intended destination. It’s a dumb mistake, but one that gives hackers the keys to the kingdom. Now go forth, and for the love of everything holy, stop writing insecure code like this.

> Stay tuned for the Part II, where we'll dive much deeper into the topics we've covered and explore more advanced concepts. Get ready for some hands-on experiments and insights that will take your understanding to the next level!
{: .prompt-tip }

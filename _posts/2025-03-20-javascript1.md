---
title: Javascript for Hackers - Chapter 1
date: 2025-03-20 07:17:00 +/-TTTT
image:
  path: /assets/img/favicons/Javasscript-Security.png
  class: "img-right"
categories: [WebSec]
tags: [WebSec]
---

# **Chapter 1: JavaScript’s Core – Understanding the Machine**  

## **1.1 JavaScript Execution: From Source Code to Machine Code**
### → How JavaScript is parsed, compiled, and executed step by step  
### → Differences between JIT compilation, interpreted execution, and bytecode  
### → How JS engines (V8, SpiderMonkey, JavaScriptCore) handle execution differently  
### → Manipulating execution flow to control JavaScript’s behavior  

## **1.2 The JavaScript Compiler – How the Code Gets Optimized (or Broken)**
### → Abstract Syntax Trees (ASTs): How JavaScript is structured internally  
### → JIT optimizations: Hidden performance tricks inside JavaScript engines  
### → How JavaScript deoptimizes itself (and how to trigger deoptimization)  
### → Crashing the compiler by confusing JIT heuristics  

## **1.3 Execution Contexts and the Call Stack – The Hidden Rules of Execution**
### → Understanding the **call stack** and function execution sequence  
### → Execution contexts: How JavaScript remembers variables across functions  
### → The `this` keyword mystery – how it changes depending on execution  
### → Overwriting execution contexts to hijack function behavior  

## **1.4 JavaScript’s Event Loop & Task Queues – Breaking Async Execution**
### → What happens inside the **event loop** (and how it controls execution order)  
### → **Microtasks vs. Macrotasks** – The hidden timing queue inside JavaScript  
### → Creating **race conditions** by manipulating event loop behavior  
### → Using `queueMicrotask()`, `requestIdleCallback()` for **stealth execution**  

## **1.5 Scopes, Closures, and Variable Leaks – Controlling JavaScript Memory**
### → How JavaScript manages **scope** and **closures** internally  
### → Leaking data across function executions using closure abuse  
### → **Hidden persistence tricks** using closures  
### → Function factories and closure-based data exfiltration  

## **1.6 Object References & Memory Management – How Garbage Collection Works**
### → JavaScript’s **garbage collector** (Mark-and-Sweep, Generational GC)  
### → **Why memory leaks happen** (and how attackers use them)  
### → Preventing object destruction to keep data persistent  
### → Stress-testing memory limits in JavaScript  

## **1.7 WeakMaps, WeakSets, and Memory Persistence – Exploiting Weak References**
### → How **WeakMaps/WeakSets** work and why they bypass garbage collection  
### → **Using WeakMaps for undetectable data storage**  
### → How malware can persist in memory using WeakRef abuse  
### → Overwriting WeakMap properties for function hijacking  

## **1.8 JavaScript Type System – How Type Coercion Can Break Everything**
### → The **difference between primitive types and reference types**  
### → How JavaScript **automatically converts types (type coercion)**  
### → Exploiting `==` vs. `===` for unexpected execution paths  
### → Attacking JSON parsing and object serialization  

## **1.9 Proxy Objects and Reflection – Hijacking JavaScript Internals**
### → How **Proxies** let you **control every JavaScript operation**  
### → Hooking property access, modifying function return values dynamically  
### → Using **Reflect API** for stealth code injection  
### → Exploiting Proxies to bypass JavaScript security mechanisms  

## **1.10 Function Hijacking & Dynamic Execution – Running Code Without `eval()`**
### → Overwriting built-in functions at runtime (`console.log`, `fetch`, `XMLHttpRequest`)  
### → Using **Function constructors** to execute arbitrary code  
### → Hooking global functions for **browser-based keylogging**  
### → How JavaScript frameworks use function hijacking internally  

## **1.11 JavaScript Execution Sandboxing – How to Escape Restrictions**
### → How JavaScript sandboxes work inside the browser  
### → Breaking `iframe` restrictions and escaping JS execution sandboxes  
### → How WebAssembly (WASM) interacts with JavaScript security  
### → Using **side-channel techniques** to leak data from sandboxes  

## **1.12 Writing Self-Modifying JavaScript – Code That Rewrites Itself**
### → How JavaScript can rewrite its own source code at runtime  
### → Using **AST manipulation** to dynamically modify scripts  
### → How obfuscators use **self-modifying code to avoid detection**  
### → **Writing a JavaScript worm** that modifies itself on execution  

## **1.13 Debugging and Hooking JavaScript Internals – Breaking and Fixing Execution**
### → How to hook into JavaScript **without modifying the source**  
### → Intercepting and modifying **function calls dynamically**  
### → Using **JavaScript debugging tools** to track execution flow  
### → Extracting hidden API calls and secrets from JavaScript  

## **1.14 JavaScript Performance Tuning and Side-Channel Exploits**
### → How JavaScript **optimizes** itself at runtime  
### → Timing attacks using **high-resolution performance timers**  
### → Extracting sensitive data by measuring JavaScript execution speed  
### → **Stealth execution techniques** to evade detection  

## **1.15 How JavaScript Handles Errors – Exploiting Try/Catch**
### → How JavaScript **handles errors internally**  
### → Exploiting **try/catch mechanisms for unexpected execution paths**  
### → How to detect and trigger hidden error states in applications  
### → Using error handling to manipulate JavaScript engines  



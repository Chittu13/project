#!/bin/bash

echo "[*] Compiling web scanner..."
g++ webscanner.cpp -o webscanner -lcurl

if [ $? -eq 0 ]; then
    echo "[+] Compilation successful! Running scanner..."
    ./webscanner
else
    echo "[!] Compilation failed."
fi

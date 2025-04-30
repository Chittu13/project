import os
import re
import subprocess
import sys
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Color Codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def typing_text(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def banner(text):
    print(f"\n{BOLD}{CYAN}{'=' * 60}")
    print(f"{BOLD}{CYAN}{text.center(60)}")
    print(f"{BOLD}{CYAN}{'=' * 60}{RESET}")

def create_directory(path):
    os.makedirs("result", exist_ok=True)
    os.makedirs(path, exist_ok=True)

def extract_domain(url):
    parsed = urlparse(url)
    domain = parsed.netloc
    if domain.startswith("www."):
        domain = domain[4:]
    return domain

def run_nmap(domain, output_path):
    banner("Running Nmap Scan (All Ports + Service Detection)")
    try:
        result = subprocess.run(
            ["nmap", "-sV", "-T4", "--open", domain],
            capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        result = e

    output = result.stdout
    filtered_output = []

    host_info = re.search(r"Nmap scan report for (.+)", output)
    if host_info:
        filtered_output.append(host_info.group(1))

    rdns_info = re.search(r"rDNS record for .+", output)
    if rdns_info:
        filtered_output.append(rdns_info.group(0))

    port_section = re.findall(r"(\d+/tcp\s+open\s+\S+\s+[^\n]+)", output)
    if port_section:
        filtered_output.append("PORT   STATE SERVICE VERSION")
        filtered_output.extend(port_section)

    with open(output_path, "w") as f:
        for line in filtered_output:
            print(f"{GREEN}{line}{RESET}")
            f.write(line + "\n")

def run_command_and_save(command, output_path):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        result = e

    with open(output_path, "w") as f:
        for line in result.stdout.splitlines():
            f.write(line + "\n")
            print(f"{CYAN}{line}{RESET}")

def get_html(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        return response.text
    except requests.RequestException:
        return ""

def normalize_url(base_url, found_url):
    return found_url if found_url.startswith("http") else urljoin(base_url, found_url)

def extract_endpoints(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    tags = soup.find_all(["a", "form", "script", "link", "img"])
    links = set()

    for tag in tags:
        for attr in ["href", "src", "action"]:
            if tag.has_attr(attr):
                links.add(normalize_url(base_url, tag[attr]))

    return sorted(links)

def extract_js_files(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    js_files = set()

    for script in soup.find_all("script", src=True):
        src = script['src']
        if src.endswith(".js"):
            js_files.add(normalize_url(base_url, src))

    return sorted(js_files)

def run_endpoint_logic(url, output_path):
    banner("Extracting Endpoints & JS Files")
    html = get_html(url)
    if not html:
        print(f"{YELLOW}[!] Failed to fetch website content.{RESET}")
        return

    endpoints = extract_endpoints(html, url)
    js_files = extract_js_files(html, url)

    with open(output_path, "w") as f:
        print(f"{GREEN}\n[+] Unique Endpoints Found:{RESET}")
        f.write("[+] Unique Endpoints Found:\n")
        for endpoint in endpoints:
            print(f"{CYAN}{endpoint}{RESET}")
            f.write(endpoint + "\n")

        print(f"{GREEN}\n[+] JavaScript Files Found:{RESET}")
        f.write("\n[+] JavaScript Files Found:\n")
        for js in js_files:
            print(f"{CYAN}{js}{RESET}")
            f.write(js + "\n")

def run_subdomain_enumeration(domain, result_dir):
    banner("Running Subdomain Enumeration")
    subfinder_cmd = f"subfinder -d {domain} -all -silent"
    assetfinder_cmd = f"assetfinder --subs-only {domain}"

    sub1 = subprocess.run(subfinder_cmd, shell=True, capture_output=True, text=True).stdout.strip().splitlines()
    sub2 = subprocess.run(assetfinder_cmd, shell=True, capture_output=True, text=True).stdout.strip().splitlines()
    all_subdomains = sorted(set(sub1 + sub2))

    if not all_subdomains:
        print(f"{YELLOW}[!] No subdomains found.{RESET}")
        return

    alive_subdomains = []
    dead_subdomains = []

    for sub in all_subdomains:
        url = f"http://{sub}"
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            if response.status_code == 200:
                alive_subdomains.append(f"{sub} [Status: {response.status_code}]")
            else:
                dead_subdomains.append(f"{sub} [Status: {response.status_code}]")
        except requests.RequestException:
            dead_subdomains.append(f"{sub} [No Response]")

    sub_file = os.path.join(result_dir, "subdomains.txt")
    with open(sub_file, "w") as f:
        f.write("[+] Alive Subdomains:\n")
        for s in alive_subdomains:
            f.write(s + "\n")
        f.write("\n[+] Dead Subdomains:\n")
        for s in dead_subdomains:
            f.write(s + "\n")

    print(f"\n{CYAN}[+] Total Subdomains Found: {len(all_subdomains)}{RESET}")
    print(f"{GREEN}[+] Alive Subdomains: {len(alive_subdomains)}{RESET}")
    print(f"{RED}[+] Dead Subdomains: {len(dead_subdomains)}{RESET}")
    print(f"{GREEN}[+] Subdomain scan saved to {sub_file}{RESET}")

def run_scan_vuln(url, output_path):
    banner("Running Vulnerability Scan")
    run_command_and_save(f"python3 scan_vuln.py pull --host {url}", output_path)

def run_param_xss_scan(domain, result_dir):
    banner("Running Parameter and XSS Scans")
    param_output = f"ParamSpider/output/{domain}.txt"
    os.makedirs("ParamSpider/output", exist_ok=True)

    try:
        subprocess.run(f"python3 ParamSpider/paramspider.py --domain {domain} --exclude png,svg,jpg", shell=True, check=True)
    except KeyboardInterrupt:
        print(f"{YELLOW}[!] Skipping ParamSpider{RESET}")

    try:
        gxss_cmd = f"cat {param_output} | Gxss -p test123 -o xss.txt"
        subprocess.run(gxss_cmd, shell=True, check=True)
    except KeyboardInterrupt:
        print(f"{YELLOW}[!] Skipping Gxss{RESET}")

    try:
        dalfox_cmd = "cat xss.txt | dalfox pipe --skip-bav"
        run_command_and_save(dalfox_cmd, os.path.join(result_dir, "xss.txt"))
    except KeyboardInterrupt:
        print(f"{YELLOW}[!] Skipping Dalfox{RESET}")

def main():
    clear_screen()
    print(f"{BOLD}{BLUE}{'=' * 60}")
    print(f"{BOLD}{BLUE}{'WebAppSec'.center(60)}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")

    typing_text(f"{CYAN}Enter the target URL (e.g., http://example.com): {RESET}", delay=0.05)
    url = input().strip()
    domain = extract_domain(url)

    if not domain:
        print(f"{YELLOW}[!] Invalid domain format.{RESET}")
        return

    result_dir = os.path.join("result", domain)
    create_directory(result_dir)

    steps = [
        ("Subdomain Enumeration", lambda: run_subdomain_enumeration(domain, result_dir)),
        ("Nmap Scan", lambda: run_nmap(domain, os.path.join(result_dir, "nmap.txt"))),
        ("WhatWeb", lambda: run_command_and_save(f"whatweb {url}", os.path.join(result_dir, "whatweb.txt"))),
        ("Endpoint Detection", lambda: run_endpoint_logic(url, os.path.join(result_dir, "endpoint.txt"))),
        ("Vulnerability Scan", lambda: run_scan_vuln(url, os.path.join(result_dir, "scan_vuln.txt"))),
        ("Parameter & XSS Scan", lambda: run_param_xss_scan(domain, result_dir)),
    ]

    for step_name, step_func in steps:
        try:
            step_func()
        except KeyboardInterrupt:
            print(f"{YELLOW}\n[!] Skipping: {step_name}{RESET}")
            continue

    print(f"\n{BOLD}{GREEN}[\u2714] All tasks completed successfully.{RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Interrupted by user. Exiting...{RESET}")


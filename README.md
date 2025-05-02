## 🔍 WebAppSec - Web Reconnaissance & Vulnerability Scanning Toolkit
#### 🧾 Overview
WebAppSec is a comprehensive automated toolkit designed to perform a full recon and vulnerability analysis on web applications. It combines powerful open-source tools with custom Python logic to enumerate subdomains, scan open ports and services, extract endpoints and JavaScript files, perform fuzzing, detect vulnerabilities like XSS and SQL injection, and identify open redirect flaws.
- This tool is best suited for bug bounty hunters, penetration testers, and security researchers.

🧰 Requirements
✅ Tools Needed:

Ensure the following tools are installed and accessible in your system’s PATH:
- python3
- pip
- nmap
- whatweb
- subfinder
- assetfinder
- dalfox
- sqlmap
- Gxss

📦 Python Libraries:
- requests
- beautifulsoup4


### 🛠 Installation
#### 🔧 Install System Tools (Linux):

```
sudo apt update
sudo apt install -y nmap whatweb python3-pip
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/tomnomnom/assetfinder@latest
go install github.com/hahwul/dalfox/v2@latest
go install github.com/KathanP19/Gxss@latest
```

#### 📦 Install Python Libraries:
```pip3 install requests beautifulsoup4```

#### Input 
![img](img/img1.png)

#### Subdomain Enumeration 
![img](img/img2.png)

#### Scanning for the open ports
![img](img/img3.png)

#### Running whatweb (website fingerprinting tool used to identify technologies and platforms a website is running on. )
![img](img/img4.png)

#### Finding All Endpoints
![img](img/img5.png)

#### Extracting All URLs from Internet 
![img](img/img6.png)

#### Finding the Vuln Parameter 
![img](img/img7.png)

#### Saving the result 
![img](img/img8.png)

#### XSS vuln found
![img](img/img9.png)

#### Running sqlmap
![img](img/img10.png)

#### Getting the Database and table names
![img](img/img11.png)

#### Finding Open Redirect Vulnerability
![img](img/img12.png)

#### Saving the all output
![img](img/img13.png)


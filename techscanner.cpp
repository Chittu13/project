#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <regex>
#include <curl/curl.h>

using namespace std;

// Callback function for CURL to store response
size_t WriteCallback(void *contents, size_t size, size_t nmemb, string *output) {
    size_t totalSize = size * nmemb;
    output->append((char *)contents, totalSize);
    return totalSize;
}

// Function to fetch HTTP headers
map<string, string> getHeaders(const string &url) {
    CURL *curl = curl_easy_init();
    map<string, string> headersMap;

    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_NOBODY, 1L); // Fetch headers only
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        string response;
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

        struct curl_slist *headers = nullptr;
        headers = curl_slist_append(headers, "User-Agent: Mozilla/5.0");
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

        CURLcode res = curl_easy_perform(curl);
        if (res == CURLE_OK) {
            regex headerRegex(R"(([\w-]+):\s*(.+))");
            smatch match;
            string::const_iterator searchStart(response.cbegin());
            while (regex_search(searchStart, response.cend(), match, headerRegex)) {
                headersMap[match[1]] = match[2];
                searchStart = match.suffix().first;
            }
        }

        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
    }

    return headersMap;
}

// Function to fetch HTML content
string getHTML(const string &url) {
    CURL *curl = curl_easy_init();
    string response;

    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
        curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L); // Follow redirects
        curl_easy_setopt(curl, CURLOPT_USERAGENT, "Mozilla/5.0");
        curl_easy_perform(curl);
        curl_easy_cleanup(curl);
    }

    return response;
}

// Function to detect technologies from headers & HTML
map<string, string> detectTechnologies(const map<string, string> &headers, const string &html) {
    map<string, string> technologies;

    // Detect CMS
    if (headers.count("X-Powered-By") && headers.at("X-Powered-By").find("WordPress") != string::npos) {
        technologies["CMS"] = "WordPress " + headers.at("X-Powered-By");
    }
    if (html.find("wp-content") != string::npos) {
        technologies["CMS"] = "WordPress";
    }

    // Detect Analytics
    if (html.find("www.google-analytics.com") != string::npos) {
        technologies["Analytics"] = "Google Analytics";
    }
    if (html.find("parsely.com") != string::npos) {
        technologies["Analytics"] = "Parse.ly";
    }

    // Detect Security Features
    if (headers.count("Strict-Transport-Security")) {
        technologies["Security"] = "HSTS";
    }
    if (html.find("www.google.com/recaptcha") != string::npos) {
        technologies["Security"] = "reCAPTCHA";
    }

    // Detect Web Servers
    if (headers.count("Server")) {
        if (headers.at("Server").find("nginx") != string::npos) {
            technologies["Web Server"] = "Nginx";
        }
        if (headers.at("Server").find("Apache") != string::npos) {
            technologies["Web Server"] = "Apache";
        }
    }

    // Detect Programming Languages
    if (headers.count("X-Powered-By")) {
        if (headers.at("X-Powered-By").find("PHP") != string::npos) {
            technologies["Programming Language"] = "PHP";
        }
    }

    // Detect Databases
    if (headers.count("X-Database") && headers.at("X-Database").find("MySQL") != string::npos) {
        technologies["Database"] = "MySQL";
    }

    // Detect JavaScript Libraries
    if (html.find("jquery") != string::npos) {
        technologies["JavaScript Library"] = "jQuery";
    }
    if (html.find("web-vitals") != string::npos) {
        technologies["JavaScript Library"] = "web-vitals";
    }

    // Detect Tag Managers
    if (html.find("googletagmanager.com") != string::npos) {
        technologies["Tag Manager"] = "Google Tag Manager";
    }

    return technologies;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        cerr << "Usage: " << argv[0] << " <target_url>" << endl;
        return 1;
    }

    string targetUrl = argv[1];

    cout << "[*] Scanning Technologies for: " << targetUrl << "\n" << endl;

    // Get headers
    map<string, string> headers = getHeaders(targetUrl);

    // Get HTML content
    string html = getHTML(targetUrl);

    // Detect technologies
    map<string, string> technologies = detectTechnologies(headers, html);

    // Display results
    cout << "\n[+] Detected Technologies:\n";
    for (const auto &tech : technologies) {
        cout << tech.first << ": " << tech.second << endl;
    }

    return 0;
}


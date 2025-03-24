#include <iostream>
#include <string>
#include <vector>
#include <set>
#include <regex>
#include <cstdlib> // For system()
#include <curl/curl.h>

using namespace std;

// Callback function for libcurl
size_t WriteCallback(void *contents, size_t size, size_t nmemb, string *output) {
    size_t totalSize = size * nmemb;
    output->append((char *)contents, totalSize);
    return totalSize;
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

// Function to normalize URLs
string normalizeURL(const string &baseUrl, const string &foundUrl) {
    if (foundUrl.find("http") == 0 || foundUrl.find("//") == 0) {
        return foundUrl; // Already absolute URL
    }
    return baseUrl + foundUrl; // Convert relative to absolute
}

// Function to extract JavaScript files
vector<string> extractJSFiles(const string &html, const string &baseUrl) {
    set<string> jsFiles;
    regex pattern(R"(src=["'](.*?\.js(\?.*?)?)["'])");
    smatch match;

    string::const_iterator searchStart(html.cbegin());
    while (regex_search(searchStart, html.cend(), match, pattern)) {
        string jsFile = normalizeURL(baseUrl, match[1]);
        jsFiles.insert(jsFile);
        searchStart = match.suffix().first;
    }

    return vector<string>(jsFiles.begin(), jsFiles.end());
}

// Function to extract unique endpoints
vector<string> extractEndpoints(const string &html, const string &baseUrl) {
    set<string> endpoints;
    regex pattern(R"((href|src|action)=["'](.*?)["'])");
    smatch match;

    string::const_iterator searchStart(html.cbegin());
    while (regex_search(searchStart, html.cend(), match, pattern)) {
        string url = normalizeURL(baseUrl, match[2]);
        endpoints.insert(url);
        searchStart = match.suffix().first;
    }

    return vector<string>(endpoints.begin(), endpoints.end());
}

int main() {
    string targetUrl;
    cout << "Enter target URL: ";
    cin >> targetUrl;

    // Get HTML content
    string html = getHTML(targetUrl);
    if (html.empty()) {
        cerr << "[!] Failed to fetch website content." << endl;
        return 1;
    }

    // Extract and display JavaScript files
    vector<string> jsFiles = extractJSFiles(html, targetUrl);
    cout << "\n[+] JavaScript Files Found:" << endl;
    for (const string &jsFile : jsFiles) {
        cout << jsFile << endl;
    }

    // Extract and display endpoints
    vector<string> endpoints = extractEndpoints(html, targetUrl);
    cout << "\n[+] Unique Endpoints Found:" << endl;
    for (const string &endpoint : endpoints) {
        cout << endpoint << endl;
    }

    // Compile techscanner.cpp inside webscanner.cpp
    cout << "\n[*] Compiling techscanner.cpp..." << endl;
    int compileStatus = system("g++ techscanner.cpp -o techscanner -lcurl");

    if (compileStatus == 0) {
        cout << "[+] Compilation successful. Running technology detection...\n" << endl;
        string command = "./techscanner " + targetUrl;
        system(command.c_str());
    } else {
        cerr << "[!] Compilation failed. Check techscanner.cpp for errors." << endl;
    }

    return 0;
}


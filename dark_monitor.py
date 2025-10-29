"""
Dark Web OSINT Monitoring Script
Purpose: Monitor dark web sites for specific keywords (threat intelligence, leaked data, etc.)
Use responsibly and legally.
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

# add proxies here and configure them 
PROXIES = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

SITES = [
    {"url": "http://vetrisvmxszntuk4rv4fx5t7gvph5mfny2wunkfzegcjgwia4upnatyd.onion/", "name": "Example Forum"},
    {"url": "http://example2.onion", "name": "Example Marketplace"},
    # To add more sites to be monitored
]

# Keywords 
KEYWORDS = [
    "data breach",
    "leaked database",
    "credentials",
    "ransomware",
    "exploit",
    # to add more keywords as needed
]

def check_tor_connection():
    """Verify Tor connection is working"""
    try:
        response = requests.get(
            'https://check.torproject.org/api/ip',
            proxies=PROXIES,
            timeout=30
        )
        data = response.json()
        if data.get('IsTor'):
            print(f"✓ Tor connection established")
            print(f"  Exit IP: {data.get('IP')}")
            return True
        else:
            print("✗ Not connected through Tor!")
            return False
    except Exception as e:
        print(f"✗ Error checking Tor connection: {e}")
        return False

def scrape_and_search(url, site_name, keywords):
    """
    Scrape a dark web site and search for keywords
    
    Args:
        url: The .onion URL to scrape
        site_name: Friendly name for the site
        keywords: List of keywords to search for
    
    Returns:
        dict: Results containing found keywords and context
    """
    results = {
        "site": site_name,
        "url": url,
        "timestamp": datetime.now().isoformat(),
        "found_keywords": [],
        "status": "success"
    }
    
    try:
        print(f"\n[*] Scraping: {site_name}")
        print(f"    URL: {url}")
        
        response = requests.get(
            url,
            proxies=PROXIES,
            timeout=60,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get all text from the page
            page_text = soup.get_text().lower()
            
            # Search for keywords
            for keyword in keywords:
                if keyword.lower() in page_text:
                    # Find context around keyword
                    context = extract_context(page_text, keyword.lower())
                    results["found_keywords"].append({
                        "keyword": keyword,
                        "context": context
                    })
                    print(f"    ✓ Found: '{keyword}'")
            
            if not results["found_keywords"]:
                print(f"    - No keywords found")
        else:
            results["status"] = f"HTTP {response.status_code}"
            print(f"    ✗ HTTP Error: {response.status_code}")
            
    except requests.exceptions.Timeout:
        results["status"] = "timeout"
        print(f"    ✗ Timeout connecting to {url}")
    except requests.exceptions.ConnectionError:
        results["status"] = "connection_error"
        print(f"    ✗ Connection failed to {url}")
    except Exception as e:
        results["status"] = f"error: {str(e)}"
        print(f"    ✗ Error: {e}")
    
    return results

def extract_context(text, keyword, context_length=150):
    """Extract text around a keyword for context"""
    index = text.find(keyword)
    if index == -1:
        return ""
    
    start = max(0, index - context_length)
    end = min(len(text), index + len(keyword) + context_length)
    
    context = text[start:end].strip()
    return f"...{context}..."

def save_results(all_results, filename="monitoring_results.json"):
    """Save monitoring results to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\n[+] Results saved to {filename}")
    except Exception as e:
        print(f"[-] Error saving results: {e}")

def send_alert(results):
    """
    Send alert when keywords are found
    Implement your notification method here (email, SMS, webhook, etc.)
    """
    for result in results:
        if result["found_keywords"]:
            print(f"\n[!] ALERT: Keywords found on {result['site']}")
            for item in result["found_keywords"]:
                print(f"    - {item['keyword']}")
                # To add notification logic here

def main():
    """Main monitoring function"""
    print("=" * 60)
    print("Dark Web OSINT Monitoring Script")
    print("=" * 60)
    
    # Check Tor connection
    if not check_tor_connection():
        print("\n[!] Please ensure Tor is running:")
        print("    sudo systemctl start tor")
        return
    
    print(f"\n[*] Monitoring {len(SITES)} sites for {len(KEYWORDS)} keywords")
    print(f"[*] Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = []
    
    # Monitor each site
    for site in SITES:
        result = scrape_and_search(site["url"], site["name"], KEYWORDS)
        all_results.append(result)
        
        # Add delay between requests to be respectful
        time.sleep(5)
    
    # Save results
    save_results(all_results)
    
    # Send alerts if keywords found
    send_alert(all_results)
    
    print("\n" + "=" * 60)
    print(f"Monitoring complete at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Monitoring interrupted by user")
    except Exception as e:
        print(f"\n[!] Unexpected error: {e}")

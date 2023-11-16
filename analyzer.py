import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse
import os

def download_file(url, folder_path="."):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            file_name = os.path.join(folder_path, os.path.basename(url))
            with open(file_name, "w", encoding="utf-8") as file:
                file.write(response.text)
            print(f"Downloaded: {url} to {file_name}")
        else:
            print(f"Error: Unable to download {url}. Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def analyze_website_performance(url, analyze_assets=True, analyze_dns=True, analyze_robots_txt=True):
    try:
        # Step 1: Fetch HTML content
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error: Unable to fetch the website. Status Code: {response.status_code}")
            return

        # Step 2: Parse HTML and extract assets (CSS, JavaScript)
        css_links, js_scripts = [], []
        if analyze_assets:
            soup = BeautifulSoup(response.content, 'html.parser')
            css_links = [link['href'] for link in soup.find_all('link', {'rel': 'stylesheet'})]
            js_scripts = [script['src'] for script in soup.find_all('script', {'src': True})]

        # Step 3: Measure page load time
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()

        if response.status_code == 200:
            page_load_time = end_time - start_time
            print(f"Page Load Time: {page_load_time:.2f} seconds")
        else:
            print(f"Error: Unable to fetch the website. Status Code: {response.status_code}")
            return

        # Step 4: Additional metrics
        server_response_time = response.elapsed.total_seconds()
        content_size_kb = len(response.content) / 1024  # in kilobytes
        num_requests = len(response.history) + 1  # include redirects

        print(f"Server Response Time: {server_response_time:.2f} seconds")
        print(f"Content Size: {content_size_kb:.2f} KB")
        print(f"Number of Requests: {num_requests}")

        # Step 5: Assets Information
        if analyze_assets:
            print("CSS Links:")
            for css_link in css_links:
                print(f"  - {css_link}")

            print("JavaScript Scripts:")
            for js_script in js_scripts:
                print(f"  - {js_script}")
                download_file(js_script, folder_path="downloaded_js")

        # Step 6: DNS Resolution Time
        if analyze_dns:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            start_time_dns = time.time()
            _ = requests.get(f"https://{domain}")
            end_time_dns = time.time()
            dns_resolution_time = end_time_dns - start_time_dns
            print(f"DNS Resolution Time: {dns_resolution_time:.2f} seconds")

        # Step 7: Download robots.txt file
        if analyze_robots_txt:
            robots_txt_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            robots_txt_response = requests.get(robots_txt_url)
            if robots_txt_response.status_code == 200:
                with open("robots.txt", "w") as robots_file:
                    robots_file.write(robots_txt_response.text)
                print("robots.txt file downloaded successfully.")
            else:
                print(f"Error downloading robots.txt. Status Code: {robots_txt_response.status_code}")

        # Step 8: Suggestions for optimization
        if page_load_time > 3:
            print("Optimization Suggestion: Consider optimizing images to reduce page load time.")

        if analyze_assets:
            if css_links:
                print("Optimization Suggestion: Minimize and concatenate CSS files to reduce the number of requests.")

            if js_scripts:
                print("Optimization Suggestion: Minimize and concatenate JavaScript files to reduce the number of requests.")

        # Step 9: Log metrics to a file
        log_metrics(url, page_load_time, server_response_time, content_size_kb, num_requests, dns_resolution_time)

    except requests.RequestException as e:
        print(f"Error: {e}")

def log_metrics(url, page_load_time, server_response_time, content_size_kb, num_requests, dns_resolution_time):
    log_filename = "performance_log.txt"
    with open(log_filename, "a") as log_file:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} - {url}\n")
        log_file.write(f"  Page Load Time: {page_load_time:.2f} seconds\n")
        log_file.write(f"  Server Response Time: {server_response_time:.2f} seconds\n")
        log_file.write(f"  Content Size: {content_size_kb:.2f} KB\n")
        log_file.write(f"  Number of Requests: {num_requests}\n")
        log_file.write(f"  DNS Resolution Time: {dns_resolution_time:.2f} seconds\n")
        log_file.write("\n")

if __name__ == "__main__":
    website_url = input("Enter the website URL to analyze: ")
    analyze_assets = input("Do you want to analyze assets? (y/n): ").lower() == 'y'
    analyze_dns = input("Do you want to analyze DNS resolution time? (y/n): ").lower() == 'y'
    analyze_robots_txt = input("Do you want to download the robots.txt file? (y/n): ").lower() == 'y'
    
    analyze_website_performance(website_url, analyze_assets, analyze_dns, analyze_robots_txt)

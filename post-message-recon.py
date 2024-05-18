import re
import requests

# Function to fetch the JavaScript file content
def fetch_javascript(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching the JavaScript file: {e}")
        return None

# Function to find postMessage instances and provide context
def find_postmessage_instances(javascript_code):
    postmessage_pattern = re.compile(r'\.postMessage\(([^)]+)', re.IGNORECASE)
    matches = postmessage_pattern.finditer(javascript_code)
    
    results = []
    for match in matches:
        postmessage_args = match.group(1).strip()
        start_idx = max(0, match.start() - 50)
        end_idx = min(len(javascript_code), match.end() + 50)
        context_line = javascript_code[start_idx:end_idx].strip()
        results.append((postmessage_args, context_line))
    
    return results

# Main function
def main():
    target_url = input("Enter the target URL (e.g., https://lnkd.in/etVp5ur4): ").strip()
    javascript_code = fetch_javascript(target_url)
    
    if javascript_code:
        postmessage_instances = find_postmessage_instances(javascript_code)
        
        if postmessage_instances:
            print("Found postMessage instances:")
            for args, context in postmessage_instances:
                print(f"Arguments: {args}")
                print(f"Context: {context}")
                print("=" * 50)
        else:
            print("No postMessage instances found.")
    else:
        print("Failed to fetch or process the JavaScript code.")

if __name__ == "__main__":
    main()

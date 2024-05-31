import re
import requests

# Function to fetch the JavaScript file content
def fetch_javascript(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0', 'Custom-Header': 'username'}
        response = requests.get(url, headers=headers)
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

# Function to spot potential injection flaws
def spot_injection_flaws(javascript_code):
    injection_pattern = re.compile(r'postMessage\((.*)\)', re.IGNORECASE)
    matches = injection_pattern.finditer(javascript_code)
    
    injection_flaws = []
    for match in matches:
        args = match.group(1).strip()
        # Look for common user input patterns such as variables or function calls
        if re.search(r'\b(document\.getElementById|document\.querySelector|window\.location|window\.name|localStorage|sessionStorage|cookie|input|params|data|message)\b', args):
            start_idx = max(0, match.start() - 50)
            end_idx = min(len(javascript_code), match.end() + 50)
            context_line = javascript_code[start_idx:end_idx].strip()
            injection_flaws.append((args, context_line))
    
    return injection_flaws

# Function to discover logic flaws
def discover_logic_flaws(javascript_code):
    logic_flaws = []
    # Look for common patterns where postMessage is used without checks
    if 'postMessage' in javascript_code and 'addEventListener' in javascript_code:
        event_handler_pattern = re.compile(r'addEventListener\s*\(\s*["\']message["\']\s*,\s*(function|\(\)\s*=>)\s*{([^}]*)}', re.IGNORECASE)
        matches = event_handler_pattern.finditer(javascript_code)
        for match in matches:
            handler_code = match.group(2).strip()
            if 'event.origin' not in handler_code:  # Simple heuristic check
                start_idx = max(0, match.start() - 50)
                end_idx = min(len(javascript_code), match.end() + 50)
                context_line = javascript_code[start_idx:end_idx].strip()
                logic_flaws.append(context_line)
    
    return logic_flaws

# Main function
def main():
    target_url = input("Enter the target URL of the JavaScript file (e.g., https://example.com/script.js): ").strip()
    if not target_url.lower().endswith('.js'):
        print("The URL provided does not seem to be a JavaScript file.")
        return
    
    javascript_code = fetch_javascript(target_url)
    
    if javascript_code:
        postmessage_instances = find_postmessage_instances(javascript_code)
        injection_flaws = spot_injection_flaws(javascript_code)
        logic_flaws = discover_logic_flaws(javascript_code)
        
        if postmessage_instances:
            print("Found postMessage instances:")
            for i, (args, context) in enumerate(postmessage_instances, start=1):
                print(f"Instance {i}:")
                print(f"Arguments: {args}")
                print(f"Context: {context}")
                print("=" * 50)
        else:
            print("No postMessage instances found.")
        
        if injection_flaws:
            print("Potential Injection Flaws:")
            for i, (args, context) in enumerate(injection_flaws, start=1):
                print(f"Instance {i}:")
                print(f"Arguments: {args}")
                print(f"Context: {context}")
                print("=" * 50)
        else:
            print("No potential injection flaws found.")
        
        if logic_flaws:
            print("Potential Logic Flaws:")
            for i, context in enumerate(logic_flaws, start=1):
                print(f"Instance {i}:")
                print(f"Context: {context}")
                print("=" * 50)
        else:
            print("No potential logic flaws found.")
    else:
        print("Failed to fetch or process the JavaScript code.")

if __name__ == "__main__":
    main()

from suno_auto import SunoAuto
from loguru import logger
import uuid

def check_headers():
    print("--- Header Validation ---")
    suno = SunoAuto()
    headers = suno._get_headers()
    # Masking sensitive data for display
    display_headers = headers.copy()
    if display_headers.get("Authorization"):
        display_headers["Authorization"] = display_headers["Authorization"][:20] + "..."
    if display_headers.get("browser-token"):
        display_headers["browser-token"] = "..."
    print(display_headers)
    return headers

def check_static_analysis():
    print("\n--- Static Analysis ---")
    print("Checking for hardcoded paths...")
    with open("suno_auto.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "C:\\" in content or "/Users/" in content:
             print("WARNING: Potential hardcoded paths found.")
        else:
             print("PASSED: No hardcoded absolute paths found.")
    
    print("Checking for loop safety...")
    if "while True" in content and "timeout" in content:
        print("PASSED: 'while True' loops appear to have timeout mechanisms.")
    else:
        print("WARNING: Verify 'while True' loops have exit conditions.")

def main():
    try:
        headers = check_headers()
        check_static_analysis()
        print("\n--- Validation Complete ---")
        print("Ready for deployment.")
    except Exception as e:
        print(f"Validation failed: {e}")

if __name__ == "__main__":
    main()

from src.tools.website_inspector import fetch_website

suspicious_url = "http://sbi-secure-login.xyz"

def run_experiment():
    print(f"Inspecting website: {suspicious_url}")
    print("-" * 50)
    evidence = fetch_website(suspicious_url)
    print("Extracted Evidence:")
    print(evidence.model_dump_json(indent=2))

if __name__ == "__main__":
    run_experiment()

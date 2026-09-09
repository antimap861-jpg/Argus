from src.tools.url_analyzer import analyze_url

suspicious_url = "http://sbi-secure-login.xyz"

def run_experiment():
    print(f"Analyzing suspicious URL: {suspicious_url}")
    print("-" * 50)
    
    indicators = analyze_url(suspicious_url)
    
    print("Extracted Indicators:")
    print(indicators.model_dump_json(indent=2))

if __name__ == "__main__":
    run_experiment()

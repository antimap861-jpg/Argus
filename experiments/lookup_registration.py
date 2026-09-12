from src.tools.registration_lookup import lookup_registration

suspicious_hostname = "sbi-secure-login.xyz"

def run_experiment():
    print(f"Looking up registration for: {suspicious_hostname}")
    print("-" * 50)
    evidence = lookup_registration(suspicious_hostname)
    print("Extracted Evidence:")
    print(evidence.model_dump_json(indent=2))

if __name__ == "__main__":
    run_experiment()

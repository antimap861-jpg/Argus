from src.tools.tls_inspector import inspect_tls

suspicious_hostname = "sbi-secure-login.xyz"

def run_experiment():
    print(f"Inspecting TLS certificate for: {suspicious_hostname}")
    print("-" * 50)
    evidence = inspect_tls(suspicious_hostname)
    print("Extracted Evidence:")
    print(evidence.model_dump_json(indent=2))

if __name__ == "__main__":
    run_experiment()

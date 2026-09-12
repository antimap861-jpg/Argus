from src.models.indicators import MessageIndicators


test_data = MessageIndicators(
    claimed_organization="SBI",
    urls=["http://sbi-secure-login.xyz"],
    urgency_detected=True,
    requested_action="Verify your account"
)

print(test_data)
print(test_data.model_dump())
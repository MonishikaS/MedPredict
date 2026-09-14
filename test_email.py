from auth import generate_otp, send_email_otp

print("\n=== HealthAI Gmail Email Test ===")

otp = generate_otp()
print("Generated OTP:", otp)

receiver = input("Enter the email where you want to receive the OTP: ").strip()

if not receiver:
    print("No email address entered.")
else:
    print(f"Sending test email to: {receiver}")

    if send_email_otp(receiver, otp):
        print("SUCCESS: Gmail SMTP accepted the email.")
        print("If it does not appear in Inbox/Spam, check Gmail search and filters.")
    else:
        print("FAILED: The email could not be sent.")
        print("Check the Gmail credentials in .env and the terminal error above.")

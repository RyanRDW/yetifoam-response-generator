#!/usr/bin/env python3
"""
Update security configurations with secure passwords and production settings
"""
import secrets
import string
import os

def generate_secure_password(length=16):
    """Generate a secure password with alphanumeric and special characters"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def update_security_configs():
    # Generate secure passwords
    staff_password = generate_secure_password(20)
    admin_password = generate_secure_password(20)
    manager_password = generate_secure_password(20)
    
    print("Generated secure passwords:")
    print(f"Staff password: {staff_password[:4]}***{staff_password[-4:]} (length: {len(staff_password)})")
    print(f"Admin password: {admin_password[:4]}***{admin_password[-4:]} (length: {len(admin_password)})")
    print(f"Manager password: {manager_password[:4]}***{manager_password[-4:]} (length: {len(manager_password)})")
    
    # Update .streamlit/secrets.toml
    secrets_content = f"""# Streamlit secrets configuration
# Production passwords - Generated {os.popen('date').read().strip()}

[auth]
# Secure production passwords
staff_password = "{staff_password}"
admin_password = "{admin_password}"
manager_password = "{manager_password}"

[app]
environment = "production"
debug_mode = false
max_results_limit = 15
rate_limit_queries_per_minute = 20

[monitoring]
enable_analytics = true
log_level = "INFO"

[data]
dataset_version = "v6.0"
quality_threshold = 0.75
"""
    
    with open('.streamlit/secrets.toml', 'w') as f:
        f.write(secrets_content)
    
    print("\nUpdated .streamlit/secrets.toml with:")
    print("- Secure passwords (20 characters with special chars)")
    print("- Production mode enabled")
    print("- Debug mode disabled")
    
    # Update config.toml for production
    config_content = """[server]
headless = true
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 50
port = 8501

[browser]
gatherUsageStats = false

[theme]
base = "light"
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[logger]
level = "INFO"
"""
    
    with open('.streamlit/config.toml', 'w') as f:
        f.write(config_content)
    
    print("Updated .streamlit/config.toml for production")
    
    return {
        'staff_password_preview': f"{staff_password[:4]}***{staff_password[-4:]}",
        'admin_password_preview': f"{admin_password[:4]}***{admin_password[-4:]}",
        'manager_password_preview': f"{manager_password[:4]}***{manager_password[-4:]}",
        'production_mode': True,
        'debug_mode': False
    }

if __name__ == "__main__":
    result = update_security_configs()
    print(f"\nSecurity update complete: {result}")
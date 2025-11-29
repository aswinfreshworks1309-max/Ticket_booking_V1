import sys
with open("import_log.txt", "w") as f:
    try:
        import pydantic_settings
        f.write("pydantic_settings: OK\n")
    except ImportError as e:
        f.write(f"pydantic_settings: FAIL {e}\n")

    try:
        import email_validator
        f.write("email_validator: OK\n")
    except ImportError as e:
        f.write(f"email_validator: FAIL {e}\n")
    
    try:
        from app.main import app
        f.write("app_import: OK\n")
    except Exception as e:
        f.write(f"app_import: FAIL {e}\n")

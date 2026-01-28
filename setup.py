#!/usr/bin/env python3
"""
Interactive setup script for SpaceWatch
Prompts users for required configuration before running the application
"""

import os
import sys
from pathlib import Path


def get_input(prompt, default=None, required=True, is_secret=False):
    """Get user input with optional default value."""
    if default:
        display_prompt = f"{prompt} [{default}]: "
    else:
        display_prompt = f"{prompt}: "
    
    while True:
        if is_secret:
            # For secret inputs, try getpass but fall back to regular input if it fails
            try:
                import getpass
                value = getpass.getpass(display_prompt)
            except Exception:
                # Fall back to regular input if getpass fails (e.g., in non-interactive mode)
                value = input(display_prompt).strip()
        else:
            value = input(display_prompt).strip()
        
        if value:
            return value
        elif default:
            return default
        elif not required:
            return ""
        else:
            print("  ⚠️  This field is required. Please provide a value.")


def setup_configuration():
    """Interactive configuration setup."""
    print("=" * 70)
    print("🚀 SpaceWatch - AI-Driven Observability Backend Setup")
    print("=" * 70)
    print()
    print("This wizard will help you configure SpaceWatch.")
    print("Press Ctrl+C at any time to cancel.")
    print()
    
    # Check if .env already exists
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  A .env file already exists.")
        overwrite = input("Do you want to overwrite it? (yes/no) [no]: ").strip().lower()
        if overwrite not in ("yes", "y"):
            print("Setup cancelled. Your existing .env file was not modified.")
            return False
        print()
    
    config = {}
    
    # Required: AI Agent Configuration
    print("📡 AI Agent Configuration (REQUIRED)")
    print("-" * 70)
    print("SpaceWatch uses an OpenAI-compatible AI agent for intelligent queries.")
    print()
    
    config["DO_AGENT_URL"] = get_input(
        "AI Agent URL (OpenAI-compatible endpoint)",
        default=None,
        required=True
    )
    
    config["DO_AGENT_KEY"] = get_input(
        "AI Agent API Key",
        default=None,
        required=True,
        is_secret=True
    )
    print()
    
    # Optional: App Security
    print("🔐 Application Security (OPTIONAL)")
    print("-" * 70)
    print("Protect your API endpoints with an API key.")
    print()
    
    config["APP_API_KEY"] = get_input(
        "API Key for protecting endpoints (leave blank to skip)",
        default=None,
        required=False,
        is_secret=True
    )
    print()
    
    # Optional: Default Spaces Configuration
    print("🌍 Default DigitalOcean Spaces Region (OPTIONAL)")
    print("-" * 70)
    print("Note: Users can override these settings per request in multi-tenant mode.")
    print()
    
    config["SPACES_REGION"] = get_input(
        "Default Spaces region",
        default="sgp1",
        required=False
    )
    
    # Auto-generate endpoint from region
    if config["SPACES_REGION"]:
        default_endpoint = f"https://{config['SPACES_REGION']}.digitaloceanspaces.com"
        config["SPACES_ENDPOINT"] = get_input(
            "Default Spaces endpoint URL",
            default=default_endpoint,
            required=False
        )
    print()
    
    # Write .env file
    print("💾 Writing configuration to .env file...")
    try:
        with open(".env", "w") as f:
            f.write("# ================================\n")
            f.write("# SpaceWatch Configuration\n")
            f.write(f"# Generated: {os.popen('date').read().strip()}\n")
            f.write("# ================================\n\n")
            
            f.write("# ================================\n")
            f.write("# AI Agent (OpenAI-compatible) - REQUIRED\n")
            f.write("# ================================\n")
            f.write(f"DO_AGENT_URL={config['DO_AGENT_URL']}\n")
            f.write(f"DO_AGENT_KEY={config['DO_AGENT_KEY']}\n\n")
            
            if config.get("APP_API_KEY"):
                f.write("# ================================\n")
                f.write("# App Security\n")
                f.write("# ================================\n")
                f.write(f"APP_API_KEY={config['APP_API_KEY']}\n\n")
            
            if config.get("SPACES_REGION"):
                f.write("# ================================\n")
                f.write("# Default Region (Optional)\n")
                f.write("# Users can override per request\n")
                f.write("# ================================\n")
                f.write(f"SPACES_REGION={config['SPACES_REGION']}\n")
                if config.get("SPACES_ENDPOINT"):
                    f.write(f"SPACES_ENDPOINT={config['SPACES_ENDPOINT']}\n")
                f.write("\n")
            
            f.write("# ================================\n")
            f.write("# NOTE: Multi-Tenant Configuration\n")
            f.write("# ================================\n")
            f.write("# DigitalOcean Spaces credentials are NO LONGER configured globally.\n")
            f.write("# Users must provide their access key, secret key, log bucket, and\n")
            f.write("# metrics bucket with each API request.\n")
            f.write("#\n")
            f.write("# This allows multi-tenant usage where each request uses its own\n")
            f.write("# credentials and accesses only its own resources.\n")
            f.write("#\n")
            f.write("# Example request headers:\n")
            f.write("#   X-Spaces-Key: your_spaces_access_key\n")
            f.write("#   X-Spaces-Secret: your_spaces_secret_key\n")
            f.write("#   X-Log-Bucket: my-access-logs\n")
            f.write("#   X-Metrics-Bucket: my-metrics-bucket\n")
            f.write("# ================================\n")
        
        print("✅ Configuration saved successfully!")
        print()
        print("=" * 70)
        print("🎉 Setup Complete!")
        print("=" * 70)
        print()
        print("You can now start SpaceWatch with:")
        print("  uvicorn main:app --host 0.0.0.0 --port 8000")
        print()
        print("Or for development with auto-reload:")
        print("  uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        print()
        print("📖 For more information, see README.md")
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error writing .env file: {e}")
        return False


if __name__ == "__main__":
    try:
        success = setup_configuration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
IBM Cloud Watsonx Foundation Model Lister
Lists all available foundation models on IBM Cloud watsonx.ai.
"""

import os
import sys
import argparse
import json
from typing import Dict, Any, List
import requests
from dotenv import load_dotenv

# Try importing tabulate for pretty terminal tables
try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

# Try importing ibm_watsonx_ai SDK
try:
    from ibm_watsonx_ai import APIClient, Credentials
    HAS_IBM_SDK = True
except ImportError:
    HAS_IBM_SDK = False


def load_environment():
    """Load environment variables from .env or ,env."""
    # Check .env first
    if os.path.exists(".env"):
        load_dotenv(".env")
    elif os.path.exists(",env"):
        load_dotenv(",env")
    else:
        load_dotenv()


def get_iam_token(api_key: str) -> str:
    """Exchange IBM Cloud API key for an IAM Bearer access token."""
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key
    }
    
    response = requests.post(iam_url, headers=headers, data=data, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to authenticate with IBM Cloud IAM (HTTP {response.status_code}):\n{response.text}"
        )
    
    token_data = response.json()
    return token_data.get("access_token")


def list_models_via_rest(api_key: str, service_url: str) -> List[Dict[str, Any]]:
    """List foundation models using direct IBM Cloud REST API."""
    token = get_iam_token(api_key)
    
    # Standard foundation model specs endpoint
    endpoint = f"{service_url.rstrip('/')}/ml/v1/foundation_model_specs?version=2023-05-29"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    response = requests.get(endpoint, headers=headers, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to retrieve models from {endpoint} (HTTP {response.status_code}):\n{response.text}"
        )
    
    data = response.json()
    return data.get("resources", [])


def list_models_via_sdk(api_key: str, service_url: str) -> List[Dict[str, Any]]:
    """List foundation models using the official ibm-watsonx-ai Python SDK."""
    if not HAS_IBM_SDK:
        raise ImportError("ibm-watsonx-ai package is not installed.")
    
    credentials = Credentials(
        url=service_url,
        api_key=api_key
    )
    client = APIClient(credentials)
    
    # Get foundation model specifications
    specs = client.foundation_models.get_model_specs()
    return specs.get("resources", [])


def format_model_data(resources: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Extract and format essential model information into clean records."""
    formatted = []
    for item in resources:
        model_id = item.get("model_id", "N/A")
        label = item.get("label", item.get("name", "N/A"))
        provider = item.get("provider", "N/A")
        
        # Extract token limits
        limits = item.get("limits", {})
        max_seq_len = limits.get("max_sequence_length", "N/A")
        max_output_tokens = limits.get("max_output_tokens", "N/A")
        
        # Extract task categories / tasks
        tasks = item.get("tasks", [])
        task_names = ", ".join([t.get("id", "") for t in tasks if isinstance(t, dict)]) if tasks else "General"
        if not task_names:
            task_names = "General"
            
        # Lifecycle status
        lifecycle = item.get("lifecycle", [])
        status = lifecycle[0].get("id", "available") if lifecycle and isinstance(lifecycle, list) else "available"
        
        formatted.append({
            "model_id": model_id,
            "label": label,
            "provider": provider,
            "max_seq_len": str(max_seq_len),
            "max_output": str(max_output_tokens),
            "tasks": task_names,
            "status": status
        })
    
    # Sort models alphabetically by provider, then model_id
    formatted.sort(key=lambda x: (x["provider"], x["model_id"]))
    return formatted


def print_table(models: List[Dict[str, str]]):
    """Print model data as a nicely formatted table in terminal."""
    if HAS_TABULATE:
        table_data = [
            [
                m["model_id"],
                m["label"],
                m["provider"],
                m["max_seq_len"],
                m["status"]
            ]
            for m in models
        ]
        headers = ["Model ID", "Label / Name", "Provider", "Max Context", "Status"]
        print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
    else:
        # Fallback simple formatted output
        print(f"{'MODEL ID':<40} | {'PROVIDER':<15} | {'MAX TOKENS':<10} | {'LABEL'}")
        print("-" * 90)
        for m in models:
            print(f"{m['model_id']:<40} | {m['provider']:<15} | {m['max_seq_len']:<10} | {m['label']}")


def main():
    parser = argparse.ArgumentParser(description="List IBM Cloud watsonx Foundation Models")
    parser.add_argument("--api-key", "-k", help="IBM Cloud API Key (or set in .env)")
    parser.add_argument("--url", "-u", help="IBM Cloud Service URL (e.g. https://us-south.ml.cloud.ibm.com)")
    parser.add_argument("--use-sdk", action="store_true", help="Use ibm-watsonx-ai SDK instead of direct REST API")
    parser.add_argument("--json", "-j", action="store_true", help="Output raw JSON results")
    parser.add_argument("--provider", "-p", help="Filter models by provider (e.g. ibm, meta, mistralai)")
    parser.add_argument("--search", "-s", help="Search model ID or name")
    args = parser.parse_args()

    load_environment()

    api_key = args.api_key or os.getenv("IBM_CLOUD_API_KEY") or os.getenv("IBM_API_KEY") or os.getenv("IBM_CLOUD_APIKEY")
    service_url = args.url or os.getenv("IBM_CLOUD_URL") or "https://us-south.ml.cloud.ibm.com"

    print("=" * 80)
    print(" 🚀 IBM Cloud Watsonx - Foundation Models Explorer")
    print("=" * 80)
    print(f"Service URL : {service_url}")
    
    if not api_key or api_key.strip() == "your_ibm_cloud_api_key_here":
        print("\n❌ Error: IBM Cloud API Key is not configured!")
        print("\nHow to set your API Key:")
        print("1. Open the '.env' file in this folder and add your key:")
        print("   IBM_CLOUD_API_KEY=your_actual_api_key_here")
        print("\n2. Or pass it directly via command line:")
        print("   python3 list_ibm_models.py --api-key YOUR_API_KEY")
        print("\n3. Or export it in your environment:")
        print("   export IBM_CLOUD_API_KEY=\"YOUR_API_KEY\"")
        print("\nNeed an IBM Cloud API Key?")
        print("-> Go to https://cloud.ibm.com/iam/apikeys and click 'Create IBM Cloud API key'")
        print("=" * 80)
        sys.exit(1)

    print(f"API Key     : {api_key[:6]}...{api_key[-4:] if len(api_key) > 10 else ''}")
    print(f"Method      : {'ibm-watsonx-ai SDK' if args.use_sdk else 'IBM Cloud REST API'}")
    print("\n⏳ Fetching available models from IBM Cloud...\n")

    try:
        if args.use_sdk:
            raw_models = list_models_via_sdk(api_key, service_url)
        else:
            raw_models = list_models_via_rest(api_key, service_url)
            
        formatted_models = format_model_data(raw_models)

        # Apply filters if requested
        if args.provider:
            formatted_models = [m for m in formatted_models if args.provider.lower() in m["provider"].lower()]
        if args.search:
            s = args.search.lower()
            formatted_models = [m for m in formatted_models if s in m["model_id"].lower() or s in m["label"].lower()]

        if args.json:
            print(json.dumps(formatted_models, indent=2))
            return

        print(f"✨ Found {len(formatted_models)} foundation models:")
        print("-" * 80)
        print_table(formatted_models)
        print("-" * 80)
        print(f"\nTotal Models: {len(formatted_models)}")
        print("Tip: Use '--search <term>' or '--provider <name>' (e.g., --provider ibm or --provider meta) to filter.")
        print("Tip: Use '--json' for JSON output.")

    except Exception as e:
        print(f"\n❌ Error connecting to IBM Cloud:\n{e}")
        print("\nTroubleshooting tips:")
        print("1. Verify that your API key is valid and has access to Watson Machine Learning / watsonx.")
        print(f"2. Ensure the region in URL is correct (current: {service_url}).")
        print("   Examples: https://us-south.ml.cloud.ibm.com, https://eu-de.ml.cloud.ibm.com, https://jp-tok.ml.cloud.ibm.com")
        sys.exit(1)


if __name__ == "__main__":
    main()

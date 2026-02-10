# Polymarket Authentication Test

This directory contains tools for testing and authenticating with the Polymarket CLOB API.

## Files

- `test_polymarket_auth.py` - Comprehensive authentication test script
- `test_auth_requirements.txt` - Python dependencies
- `working_auth_config.json` - Generated when auth succeeds (working config)

## Setup

1. Install dependencies:
```bash
pip install -r test_auth_requirements.txt
```

2. Set your API credentials as environment variables:
```bash
# Windows Command Prompt
set POLYMARKET_API_KEY=your-api-key-here
set POLYMARKET_API_SECRET=your-api-secret-here

# Windows PowerShell
$env:POLYMARKET_API_KEY="your-api-key-here"
$env:POLYMARKET_API_SECRET="your-api-secret-here"

# Linux/Mac
export POLYMARKET_API_KEY="your-api-key-here"
export POLYMARKET_API_SECRET="your-api-secret-here"
```

## Usage

Run the test script:
```bash
python test_polymarket_auth.py
```

The script will try multiple authentication methods:
1. Basic header authentication (various header formats)
2. Timestamp-based HMAC signing
3. EIP-712 Ethereum message signing (requires eth-account)
4. JWT token exchange
5. Request body authentication
6. Swapped credentials
7. Query parameter authentication
8. Session/cookie authentication

## Output

When a working method is found, the script will:
- Display the successful authentication method
- Show the working headers
- Save the configuration to `working_auth_config.json`
- Provide example Python code for other agents to use

## Troubleshooting

If all methods fail:
- Verify your API credentials are correct
- Check that you have the correct API key and secret from Polymarket
- Ensure the API endpoint hasn't changed
- Try accessing https://clob.polymarket.com directly to verify connectivity

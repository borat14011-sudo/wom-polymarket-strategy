# Kimi Model Stack - Environment Setup
# Add these to your PowerShell profile or run before using HuggingFace models

# HuggingFace API Key (required for HF models)
$env:HF_API_KEY = "your_huggingface_token_here"

# Optional: Set default model preferences per task type
$env:OPENCLAW_TRADING_STRATEGIC = "moonshot/kimi-k2.5"
$env:OPENCLAW_TRADING_EXECUTION = "moonshot/kimi-k2-0905-preview"
$env:OPENCLAW_TRADING_ANALYSIS = "huggingface/moonshotai/Kimi-K2-Thinking"
$env:OPENCLAW_TRADING_QUICK = "huggingface/moonshotai/Kimi-K2-Instruct-7B"

Write-Host "✅ Kimi model environment configured" -ForegroundColor Green
Write-Host "   Strategic: $env:OPENCLAW_TRADING_STRATEGIC" -ForegroundColor Cyan
Write-Host "   Execution: $env:OPENCLAW_TRADING_EXECUTION" -ForegroundColor Cyan
Write-Host "   Analysis:  $env:OPENCLAW_TRADING_ANALYSIS" -ForegroundColor Cyan
Write-Host "   Quick:     $env:OPENCLAW_TRADING_QUICK" -ForegroundColor Cyan

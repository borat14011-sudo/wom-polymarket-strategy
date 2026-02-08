# 🚀 Kimi Model Stack - Quick Reference

## Models Configured

| Alias | Full Path | Best For | Cost/1M |
|-------|-----------|----------|---------|
| `Kimi Strategic` | `moonshot/kimi-k2.5` | Complex strategies, architecture | $2/$8 |
| `Kimi Default` | `moonshot/kimi-k2-0905-preview` | Daily tasks, default | $1/$4 |
| `Kimi Thinking` | `huggingface/moonshotai/Kimi-K2-Thinking` | Deep analysis | $1.50/$6 |
| `Kimi 7B` | `huggingface/moonshotai/Kimi-K2-Instruct-7B` | Quick tasks | $0.20/$0.80 |

## Quick Commands

```powershell
# View all models
openclaw models list

# Test a specific model (via agent)
openclaw agent --local --message "Hello"
```

## Usage by Task

### 💰 Trading
- **Strategy Design** → `moonshot/kimi-k2.5`
- **Trade Logic** → `moonshot/kimi-k2-0905-preview`
- **Sentiment Analysis** → `huggingface/moonshotai/Kimi-K2-Thinking`
- **Quick Checks** → `huggingface/moonshotai/Kimi-K2-Instruct-7B`

### 📝 Content
- **Long Articles** → `moonshot/kimi-k2.5`
- **Blog Posts** → `moonshot/kimi-k2-0905-preview`
- **Research** → `huggingface/moonshotai/Kimi-K2-Thinking`
- **Social Media** → `huggingface/moonshotai/Kimi-K2-Instruct-7B`

## Setup Required

1. **Moonshot models** - Already configured ✓
2. **HuggingFace models** - Need HF_API_KEY:
   ```powershell
   $env:HF_API_KEY = "your_token_here"
   ```
   Get token at: https://huggingface.co/settings/tokens

## Files
- Full guide: `KIMI_MODEL_GUIDE.md`
- Environment script: `kimi-models-env.ps1`
- Config: `~/.openclaw/openclaw.json`

---
*Last updated: 2025-02-08*

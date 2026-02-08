# 🤖 Kimi Model Stack - Usage Guide

Optimized configuration for Polymarket trading and content creation workflows.

---

## 📊 Model Overview

| Model | Provider | Purpose | Context | Cost/1M Tokens | Speed |
|-------|----------|---------|---------|----------------|-------|
| **Kimi K2.5** | Moonshot | Strategic reasoning | 256K | $2/$8 | Medium |
| **Kimi K2 0905** | Moonshot | Default execution | 256K | $1/$4 | Fast |
| **Kimi K2 Thinking** | HuggingFace | Deep analysis | 128K | $1.50/$6 | Slow |
| **Kimi K2 7B** | HuggingFace | Quick tasks | 32K | $0.20/$0.80 | Very Fast |

---

## 🎯 Use Case Mapping

### 💰 Polymarket Trading

| Task | Recommended Model | Why |
|------|------------------|-----|
| **Market strategy design** | `moonshot/kimi-k2.5` | Complex reasoning, position sizing, risk analysis |
| **Trade execution logic** | `moonshot/kimi-k2-0905-preview` | Reliable, fast, cost-effective |
| **Market sentiment analysis** | `huggingface/moonshotai/Kimi-K2-Thinking` | Deep analysis of news/social signals |
| **Quick price checks** | `huggingface/moonshotai/Kimi-K2-Instruct-7B` | Instant responses, minimal cost |
| **Portfolio summaries** | `huggingface/moonshotai/Kimi-K2-Instruct-7B` | Fast daily/weekly reports |
| **Risk assessment** | `moonshot/kimi-k2.5` | Thorough evaluation of exposure |

### 📝 Content Creation

| Task | Recommended Model | Why |
|------|------------------|-----|
| **Long-form articles** | `moonshot/kimi-k2.5` | High coherence, structured thinking |
| **Blog posts** | `moonshot/kimi-k2-0905-preview` | Good balance of quality and speed |
| **Research synthesis** | `huggingface/moonshotai/Kimi-K2-Thinking` | Deep reasoning, multiple sources |
| **Social media** | `huggingface/moonshotai/Kimi-K2-Instruct-7B` | Quick, punchy content |
| **Editing/proofreading** | `moonshot/kimi-k2-0905-preview` | Reliable grammar and style |
| **Content strategy** | `moonshot/kimi-k2.5` | Big picture planning |

---

## ⚡ Quick Reference Commands

### Switch Models Temporarily
```bash
# For a single command
--model moonshot/kimi-k2.5

# Check current model
openclaw status
```

### Set Model in Agent Config
Edit `agents/main/agent/models.json` or use the inline model specification.

---

## 💡 Cost Optimization Tips

### Tiered Approach
1. **Start with 7B** for initial exploration or simple queries
2. **Escalate to 0905** for production tasks
3. **Use K2.5** for complex strategic decisions
4. **Reserve Thinking** for deep research only

### Example Workflow
```
Quick market scan → 7B
Identify opportunity → 0905
Deep analysis → Thinking
Strategy formulation → K2.5
Execution → 0905
Daily summary → 7B
```

### Estimated Monthly Costs (Heavy Usage)
- **7B only**: ~$5-15
- **0905 default**: ~$20-50
- **K2.5 strategic**: ~$50-100
- **Thinking research**: ~$30-80
- **Mixed optimal**: ~$40-80

---

## 🔧 Configuration Details

### Provider Setup

**Moonshot (Direct API)**
- Base URL: `https://api.moonshot.ai/v1`
- API Key: Configured in auth profiles
- Models: k2.5, k2-0905-preview

**HuggingFace (via Novita)**
- Base URL: `https://router.huggingface.co/novita`
- API Key: Requires HF_API_KEY environment variable
- Models: K2-Thinking, K2-Instruct-7B

### Environment Variables
```bash
# Add to your shell profile
export HF_API_KEY="your_huggingface_token_here"
```

---

## 📈 Performance Characteristics

### Latency (Approximate)
| Model | First Token | Full Response (500 tokens) |
|-------|-------------|---------------------------|
| 7B | 50-100ms | 1-2s |
| 0905 | 100-200ms | 2-3s |
| K2.5 | 200-400ms | 3-5s |
| Thinking | 500ms-1s | 5-10s |

### Quality Ranking
1. **K2.5** - Best for complex reasoning
2. **Thinking** - Best for analytical tasks with explanations
3. **0905** - Solid all-rounder
4. **7B** - Good for simple tasks, fastest

---

## 🧪 Testing Commands

Test each model:

```bash
# Test strategic reasoning
openclaw run --model moonshot/kimi-k2.5 "Analyze the risk factors in Polymarket crypto prediction markets"

# Test standard execution
openclaw run --model moonshot/kimi-k2-0905-preview "Summarize current Polymarket trends"

# Test deep analysis
openclaw run --model huggingface/moonshotai/Kimi-K2-Thinking "What are the structural factors affecting prediction market accuracy?"

# Test quick tasks
openclaw run --model huggingface/moonshotai/Kimi-K2-Instruct-7B "List 3 hot Polymarket markets today"
```

---

## 🚨 Troubleshooting

### HuggingFace Model Not Responding
- Verify HF_API_KEY is set
- Check internet connectivity
- Novita router may have rate limits

### Model Selection Not Working
- Check `openclaw status` for current model
- Verify model ID spelling
- Check provider configuration in models.json

### Cost Spikes
- Use 7B for iterative exploration
- Switch to 0905 for refinement
- Reserve K2.5 for final decisions only

---

## 📝 Changelog

**2025-02-08**: Initial optimized stack configuration
- Added cost estimates
- Mapped trading/content use cases
- Created tiered workflow recommendations

---

## 🔗 Quick Links

- [Moonshot Console](https://platform.moonshot.cn/)
- [HuggingFace Inference](https://huggingface.co/docs/api-inference/index)
- [Polymarket](https://polymarket.com)

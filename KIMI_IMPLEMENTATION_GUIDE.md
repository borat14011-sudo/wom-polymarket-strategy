# Kimi Model Stack Implementation Guide

## Quick Start Configuration

### 1. Basic Model Setup
```bash
# Set up your model hierarchy
openclaw models add moonshot/kimi-k2-0905-preview --alias kimi-strategic --tier premium
openclaw models add anthropic/claude-sonnet-4-5 --alias kimi-execution --tier standard  
openclaw models add anthropic/claude-haiku-4-5 --alias kimi-budget --tier budget
```

### 2. Configuration File Setup
Create `~/.openclaw/model-config.json`:
```json
{
  "model_stack": {
    "premium": {
      "model": "moonshot/kimi-k2-0905-preview",
      "alias": "kimi-strategic",
      "max_tokens": 250000,
      "temperature": 0.7,
      "use_cases": ["strategic_analysis", "complex_reasoning", "creative_work"]
    },
    "standard": {
      "model": "anthropic/claude-sonnet-4-5", 
      "alias": "kimi-execution",
      "max_tokens": 195000,
      "temperature": 0.5,
      "use_cases": ["code_tasks", "analysis", "content_creation"]
    },
    "budget": {
      "model": "anthropic/claude-haiku-4-5",
      "alias": "kimi-budget", 
      "max_tokens": 195000,
      "temperature": 0.3,
      "use_cases": ["quick_queries", "simple_tasks", "high_volume"]
    }
  },
  "selection_rules": {
    "task_keywords": {
      "premium": ["strategic", "complex", "analysis", "planning", "creative", "synthesis"],
      "standard": ["code", "document", "summary", "review", "debug", "explain"],
      "budget": ["quick", "simple", "basic", "format", "check", "list"]
    }
  }
}
```

## Task Classification Implementation

### Python Task Classifier
```python
import json
import re

class KimiModelSelector:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def classify_task(self, task_description):
        """Classify task and return appropriate model"""
        task_lower = task_description.lower()
        
        # Check for premium keywords
        for keyword in self.config['selection_rules']['task_keywords']['premium']:
            if keyword in task_lower:
                return self.config['model_stack']['premium']
        
        # Check for standard keywords  
        for keyword in self.config['selection_rules']['task_keywords']['standard']:
            if keyword in task_lower:
                return self.config['model_stack']['standard']
        
        # Default to budget
        return self.config['model_stack']['budget']
    
    def get_model_for_task(self, task_description):
        """Get model configuration for task"""
        model_config = self.classify_task(task_description)
        return model_config['model'], model_config['alias']

# Usage example
selector = KimiModelSelector('~/.openclaw/model-config.json')
model, alias = selector.get_model_for_task("Analyze the competitive landscape for our product strategy")
print(f"Selected model: {model} (alias: {alias})")
```

## Cost Monitoring Dashboard

### Usage Tracking Script
```python
import datetime
import json
import csv

class CostTracker:
    def __init__(self):
        self.usage_log = []
        
    def log_usage(self, model, tokens_in, tokens_out, task_type, cost_estimate):
        """Log model usage for cost tracking"""
        entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'model': model,
            'tokens_in': tokens_in,
            'tokens_out': tokens_out, 
            'task_type': task_type,
            'cost_estimate': cost_estimate
        }
        self.usage_log.append(entry)
        
        # Save to file
        with open('kimi_usage_log.json', 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def generate_cost_report(self, period='daily'):
        """Generate cost analysis report"""
        # Aggregate by model tier
        tier_costs = {
            'premium': {'usage': 0, 'cost': 0},
            'standard': {'usage': 0, 'cost': 0}, 
            'budget': {'usage': 0, 'cost': 0}
        }
        
        # Model pricing (approximate)
        pricing = {
            'moonshot/kimi-k2-0905-preview': 0.045,  # per 1K tokens
            'anthropic/claude-sonnet-4-5': 0.02,
            'anthropic/claude-haiku-4-5': 0.002
        }
        
        for entry in self.usage_log:
            model = entry['model']
            tokens = entry['tokens_in'] + entry['tokens_out']
            cost = (tokens / 1000) * pricing.get(model, 0.02)
            
            # Determine tier
            if 'kimi-k2' in model:
                tier = 'premium'
            elif 'sonnet' in model:
                tier = 'standard'  
            else:
                tier = 'budget'
                
            tier_costs[tier]['usage'] += 1
            tier_costs[tier]['cost'] += cost
        
        return tier_costs

# Usage
tracker = CostTracker()
# Log each API call
tracker.log_usage('moonshot/kimi-k2-0905-preview', 1500, 800, 'strategic_analysis', 0.103)
```

## Automated Workflow Examples

### 1. Smart Task Router
```bash
#!/bin/bash
# smart-router.sh

task_description="$1"

# Simple keyword-based routing
if echo "$task_description" | grep -qi "strategic\|complex\|analysis\|planning"; then
    echo "Routing to Kimi K2 (Premium)"
    openclaw run --model moonshot/kimi-k2-0905-preview "$task_description"
elif echo "$task_description" | grep -qi "code\|document\|summary\|review"; then
    echo "Routing to Claude Sonnet (Standard)"  
    openclaw run --model anthropic/claude-sonnet-4-5 "$task_description"
else
    echo "Routing to Claude Haiku (Budget)"
    openclaw run --model anthropic/claude-haiku-4-5 "$task_description"
fi
```

### 2. Progressive Escalation System
```python
import subprocess
import json

def progressive_query(task, max_escalations=2):
    """Try budget model first, escalate if needed"""
    
    models_to_try = [
        ('anthropic/claude-haiku-4-5', 'budget'),
        ('anthropic/claude-sonnet-4-5', 'standard'), 
        ('moonshot/kimi-k2-0905-preview', 'premium')
    ]
    
    for model, tier in models_to_try[:max_escalations + 1]:
        print(f"Trying {tier} model: {model}")
        
        # Simulate API call
        result = mock_api_call(model, task)
        
        # Check if result quality is sufficient
        if assess_result_quality(result) >= 0.8:
            print(f"Success with {tier} model")
            return result, model, tier
        
        print(f"Insufficient quality from {tier} model, escalating...")
    
    return result, model, 'premium'  # Return best effort

def mock_api_call(model, task):
    """Simulate API call - replace with actual implementation"""
    return f"Response from {model} for task: {task}"

def assess_result_quality(result):
    """Assess if result meets quality threshold"""
    # Simple heuristic - check length and specificity
    if len(result) > 100 and any(word in result.lower() for word in ['analysis', 'solution', 'recommendation']):
        return 0.9
    return 0.6

# Usage
result, model, tier = progressive_query("Analyze market trends for Q1 2025")
```

## Integration with OpenClaw

### 1. Custom Agent Configuration
Create `~/.openclaw/agents/main/agent/model-selector.js`:
```javascript
class ModelSelector {
    constructor() {
        this.modelTiers = {
            premium: 'moonshot/kimi-k2-0905-preview',
            standard: 'anthropic/claude-sonnet-4-5',
            budget: 'anthropic/claude-haiku-4-5'
        };
        
        this.keywords = {
            premium: ['strategic', 'complex', 'analysis', 'planning', 'creative'],
            standard: ['code', 'document', 'summary', 'review', 'debug'],
            budget: ['quick', 'simple', 'basic', 'format', 'check']
        };
    }
    
    selectModel(taskDescription) {
        const lowerTask = taskDescription.toLowerCase();
        
        for (const [tier, keywords] of Object.entries(this.keywords)) {
            if (keywords.some(keyword => lowerTask.includes(keyword))) {
                return this.modelTiers[tier];
            }
        }
        
        return this.modelTiers.budget; // Default to budget
    }
}

module.exports = ModelSelector;
```

### 2. Usage Commands
```bash
# Quick commands for different tiers
alias kimi-strategic='openclaw run --model moonshot/kimi-k2-0905-preview'
alias kimi-execution='openclaw run --model anthropic/claude-sonnet-4-5'  
alias kimi-budget='openclaw run --model anthropic/claude-haiku-4-5'

# Smart selection based on task file
kimi-smart() {
    local task_file="$1"
    local task_content=$(cat "$task_file")
    
    # Simple classification
    if echo "$task_content" | grep -qi "strategic\|complex\|analysis"; then
        kimi-strategic "$task_content"
    elif echo "$task_content" | grep -qi "code\|document\|summary"; then
        kimi-execution "$task_content"
    else
        kimi-budget "$task_content"
    fi
}
```

## Best Practices

### 1. Cost Management
- Set monthly spending limits per tier
- Monitor usage patterns and adjust thresholds
- Use budget models for prototyping and testing
- Implement usage quotas for different user types

### 2. Quality Assurance
- Regular quality audits across all tiers
- A/B testing between models for similar tasks
- User feedback collection and analysis
- Performance benchmarking

### 3. Scaling Considerations
- Implement caching for frequent queries
- Use batch processing for high-volume tasks
- Consider regional deployment for latency
- Plan for enterprise usage scaling

### 4. Security and Privacy
- Implement data classification (public, internal, confidential)
- Use appropriate models for sensitive data
- Audit data retention policies
- Ensure compliance with data protection regulations

This implementation guide provides a complete framework for deploying and managing the Kimi model stack efficiently while optimizing for both cost and performance.
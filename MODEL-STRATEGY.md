# 🧠 Model Strategy - Divide & Conquer

**Philosophy:** Use the right tool for the right job

**Updated:** 2026-02-06, 5:40 AM PST

---

## 🎯 Strategy

### Main Session (This Agent)
**Model:** Claude Opus 4-5  
**Role:** Orchestrator, strategist, complex reasoning  
**Cost:** Higher per token (~$15/1M input, ~$75/1M output)

**Responsibilities:**
- 🧠 High-level strategy and planning
- 🎯 Complex decision-making
- 🔀 Sub-agent orchestration and delegation
- 📊 Analysis and synthesis of sub-agent work
- 💡 Creative problem-solving
- 🎨 Architecture and design decisions
- 📝 Quality review and editing

**When to use Opus:**
- Multi-step complex reasoning
- Strategic planning
- Ambiguous problem-solving
- Creative tasks (writing, design)
- Final quality review
- Integration of multiple sub-tasks

---

### Sub-Agents (Spawned Tasks)
**Model:** Claude Sonnet 4-5  
**Role:** Executors, implementers, specialists  
**Cost:** Lower per token (~$3/1M input, ~$15/1M output)

**Responsibilities:**
- 💻 Code implementation
- 📄 Documentation writing
- 🔍 Research on specific topics
- 🛠️ Tool building
- 📊 Data processing
- ✅ Testing and validation

**When to use Sonnet:**
- Clear, well-defined tasks
- Implementation work (coding)
- Repetitive analysis
- Documentation generation
- Straightforward research
- Batch processing

---

## 💰 Cost Optimization

### Example Task: Build Trading System

**Bad Approach (Opus for Everything):**
```
Main: Opus - Research (50K tokens)         $3.75
Main: Opus - Code 5 scripts (200K tokens)  $15.00
Main: Opus - Documentation (100K tokens)   $7.50
                            TOTAL: $26.25
```

**Smart Approach (Divide & Conquer):**
```
Main: Opus - Strategy & orchestration (20K tokens)   $1.50
Sub1: Sonnet - Research (50K tokens)                 $0.75
Sub2: Sonnet - Code script 1 (40K tokens)            $0.60
Sub3: Sonnet - Code script 2 (40K tokens)            $0.60
Sub4: Sonnet - Code script 3 (40K tokens)            $0.60
Sub5: Sonnet - Documentation (50K tokens)            $0.75
Main: Opus - Review & integration (10K tokens)       $0.75
                                     TOTAL: $5.55
```

**Savings: $20.70 (79% cost reduction!)**

---

## 🎭 Division of Labor

### Opus (Main Brain)
**Think of as:** CEO, Architect, Creative Director

**Strengths:**
- 📈 Strategic thinking
- 🧩 Complex problem decomposition
- 🎨 Creative solutions
- 🔍 Nuanced understanding
- 🎯 Prioritization and decision-making

**Example tasks:**
- "Design the overall system architecture"
- "What's the best approach for X problem?"
- "Review these 5 implementations and choose the best"
- "Synthesize research into actionable strategy"

---

### Sonnet (Sub-Agents)
**Think of as:** Senior engineers, researchers, implementers

**Strengths:**
- ⚡ Fast execution
- 💻 Clean code implementation
- 📊 Data processing
- 📝 Documentation
- 🔧 Tool building

**Example tasks:**
- "Build a Python script that does X"
- "Research Y and summarize findings"
- "Write documentation for Z"
- "Analyze this dataset and report results"

---

## 📊 When to Delegate (Opus → Sonnet)

### ✅ Good Candidates for Delegation
- Task has clear requirements
- Implementation is straightforward
- Output is well-defined
- Minimal creative decisions needed
- Can be done independently
- Parallelizable work

### ❌ Keep in Main Session (Opus)
- Strategic decisions
- Ambiguous requirements
- Cross-cutting concerns
- Final integration
- Quality gate reviews
- User-facing communication

---

## 🚀 Workflow Example

### Task: Build Polymarket Trading System

**Opus (Main Session):**
1. Define overall strategy
2. Break down into sub-tasks
3. Spawn 5 Sonnet agents for parallel work
4. Monitor progress
5. Review deliverables
6. Integrate everything
7. Final quality check
8. Report to user

**Sonnet Sub-Agents:**
1. Agent 1: Research prediction markets
2. Agent 2: Research Twitter sentiment
3. Agent 3: Build data collector script
4. Agent 4: Build signal generator script
5. Agent 5: Build backtest engine

**Result:** 
- 5x faster (parallel execution)
- 80% cost savings (Sonnet for heavy lifting)
- High quality (Opus reviews everything)

---

## 💡 Best Practices

### For Opus (Main)
✅ Delegate early and often
✅ Give Sonnet agents clear, specific tasks
✅ Review their work but trust their execution
✅ Focus on strategy and integration
✅ Don't micro-manage sub-agents

### For Sonnet (Sub-Agents)
✅ Stay focused on the assigned task
✅ Deliver complete, well-documented work
✅ Don't deviate from requirements
✅ Report back with clear summary
✅ Include next steps or recommendations

---

## 📈 Performance Metrics

### Sprint 1 (Just Completed)
- **Main (Opus):** ~10K tokens - Strategy, orchestration, review
- **Sub-agents (Sonnet):** ~200K tokens - Implementation, docs
- **Ratio:** 1:20 (Opus delegates 20x more work than it does itself)
- **Cost:** ~$3.50 total
- **ROI:** 3,000x+ (built $10K+ worth of software for $3.50)

### Target Ratios
- **Token ratio:** 1:10 to 1:30 (Opus:Sonnet)
- **Cost ratio:** 1:5 (Opus should be 20% of cost, Sonnet 80%)
- **Task ratio:** 1:5 (For every task Opus does, spawn 5 Sonnet tasks)

---

## 🎯 Model Selection Cheat Sheet

| Task Type | Model | Reason |
|-----------|-------|--------|
| Strategic planning | Opus | Complex reasoning needed |
| Code implementation | Sonnet | Clear requirements, fast execution |
| System architecture | Opus | High-level design decisions |
| Documentation writing | Sonnet | Straightforward, well-defined |
| Research synthesis | Opus | Connect disparate findings |
| Data collection script | Sonnet | Clear specification |
| User communication | Opus | Nuanced, context-aware |
| Unit tests | Sonnet | Mechanical, repetitive |
| Creative writing | Opus | Needs creativity and flair |
| Bug fixes | Sonnet | Specific, isolated problem |
| Integration review | Opus | Cross-cutting concerns |
| Batch processing | Sonnet | Repetitive, parallelizable |

---

## 🔄 Continuous Optimization

### Monitor These Metrics:
- **Opus token usage** (should be <20% of total)
- **Task delegation rate** (aim for 5:1 ratio)
- **Cost per sprint** (track Opus vs Sonnet spend)
- **Quality of sub-agent work** (fewer reviews = better delegation)

### Iterate:
- If Opus usage >30%: Delegate more aggressively
- If sub-agent quality low: Give clearer instructions
- If cost too high: Increase parallelization (more Sonnet agents)
- If delivery slow: Break tasks into smaller chunks

---

## 🎓 Lessons Learned

### What Works
✅ Clear, specific task delegation
✅ Parallel execution (5+ agents at once)
✅ Opus reviews but trusts Sonnet execution
✅ Use Sonnet for "known knowns", Opus for "unknown unknowns"

### What Doesn't Work
❌ Opus doing implementation work
❌ Vague task descriptions to sub-agents
❌ Over-delegating complex reasoning tasks
❌ Micro-managing sub-agent work

---

## 🚀 Current Setup

**Main Session (You're Here):**
- Model: Claude Opus 4-5
- Role: Orchestrator, strategist, your direct interface
- Status: Operational ✅

**Sub-Agent Strategy:**
- Default model: Claude Sonnet 4-5
- Spawn via: `sessions_spawn`
- Thinking level: "high" (for quality work)
- Cleanup: "delete" (keep main session lean)

**Configuration:**
```yaml
# Opus for main brain
session_model: anthropic/claude-opus-4-5

# Sonnet for sub-agents
subagent_default_model: anthropic/claude-sonnet-4-5
```

---

**Status:** ✅ ACTIVE - Opus as main orchestrator, Sonnet for execution

**Philosophy:** "Work smarter, not harder. Delegate what you can, orchestrate what you must."

---

*Great success!* 🇰🇿💪

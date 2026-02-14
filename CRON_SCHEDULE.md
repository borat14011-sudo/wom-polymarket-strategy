# CRON JOB SCHEDULE - Staying On Task
**Created:** February 10, 2026, 5:39 PM PST

---

## 🕐 Scheduled Tasks

| Job Name | Frequency | Model | Purpose |
|----------|-----------|-------|---------|
| **Daily Strategy Review - R1** | 9:00 AM daily | DeepSeek R1 | Review positions, market conditions, opportunities |
| **Hourly Market Monitor Check** | Every hour | Kimi K2 | Ensure agents running, data fresh, alerts handled |
| **Weekly System Audit** | Monday 10:00 AM | Kimi K2.5 | Review cron jobs, agent performance, data gaps |
| **Bi-Weekly Capital Review** | Every 14 days | DeepSeek R1 | Portfolio performance, risk exposure, capital allocation |

---

## 🔄 Continuous Monitoring Stack

### Already Running:
1. **Event Extraction Engine** - Every 30 min (cron)
2. **Market Monitor** - Every 5 min (agent)
3. **Opportunity Scanner** - Every 2 hours (agent)
4. **Event Watcher** - Every hour (agent)
5. **Price Action Analyzer** - Every 30 min (agent)
6. **Correlation Tracker** - Every 2 hours (agent)

### New Cron Oversight:
1. **Hourly Health Check** - Verifies all above are running
2. **Daily Deep Dive** - R1 strategy evaluation
3. **Weekly Audit** - System maintenance
4. **Bi-Weekly Capital** - Risk management

---

## 🎯 Focus Areas

### Daily (R1):
- Position review
- Market condition assessment
- Opportunity evaluation
- Capital allocation adjustments

### Hourly:
- Agent status checks
- Data freshness verification
- Alert monitoring
- System health

### Weekly:
- Cron job performance
- Agent metrics
- Memory completeness
- Data gap identification
- System improvements

### Bi-Weekly:
- Portfolio performance
- Risk exposure vs limits
- Drawdown monitoring
- Position sizing review
- Capital reallocation

---

## ⚙️ Technical Details

**Cron Jobs:**
1. `7d0ca86b-ab30-46e9-bce7-8c4447fd1ded` - Daily Strategy Review
2. `0e63cb77-2418-4dac-9af4-b11961151df5` - Hourly Monitor Check
3. `41119704-bfe9-4c90-9303-3690e7ab4d6a` - Weekly System Audit
4. `b9258290-dc6a-499e-8d71-2375330be0cf` - Bi-Weekly Capital Review

**Time Zone:** America/Los_Angeles (PST/PDT)

**Model Allocation:**
- **DeepSeek R1:** Complex reasoning tasks (strategy, capital)
- **Kimi K2.5:** Deep analysis (audits)
- **Kimi K2:** Lightweight monitoring (health checks)

---

## 📊 Expected Outputs

| Schedule | Deliverable | Channel |
|----------|-------------|---------|
| Daily | Strategy recommendations | Telegram |
| Hourly | System status report | Telegram (if issues) |
| Weekly | Audit findings | Telegram |
| Bi-Weekly | Capital allocation plan | Telegram |

---

## 🚨 Alert Triggers

**Immediate Alerts (via agents):**
- Price moves >2% (Tariff), >5% (Deportation), >10% (High-volume)
- Breaking news affecting markets
- Agent failures
- Data staleness (>30 min)

**Scheduled Reports:**
- Daily strategy updates
- Weekly system health
- Bi-weekly risk assessment

---

## 🔧 Maintenance

**To modify schedule:**
```bash
openclaw cron update --job-id <id> --patch '{"schedule": {...}}'
```

**To view status:**
```bash
openclaw cron list
```

**To run manually:**
```bash
openclaw cron run --job-id <id>
```

---

## 📈 Success Metrics

1. **Uptime:** All agents running 24/7
2. **Freshness:** Data <30 minutes old
3. **Coverage:** All 200 markets monitored
4. **Response:** Alerts within 5 minutes
5. **Performance:** Positive EV on trades

---

*System designed for autonomous operation with human oversight.*

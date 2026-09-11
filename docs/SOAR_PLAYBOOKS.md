# SOAR Response Playbooks & Automated Response Engine Specification

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: SOAR Architecture, Human Approval Workflow, & Simulation Mode  

---

## 1. SOAR Response Architecture & Workflow

```
[ SIEM Alert Trigger ]
          ↓
[ AI Copilot Playbook Recommendation ]
          ↓
[ Analyst Action Preview & Human Approval Step ]
          ↓
[ SOAR Execution Engine (Safe Action Allowlist) ]
          ↓
[ Action Result Verification & Incident State Update ]
          ↓
[ Audit Trail Log (PLAYBOOK_EXECUTED, ACTION_APPROVED) ]
```

---

## 2. Safe Action Allowlist & Simulation Mode

To prevent arbitrary code execution, destructive system modifications, or user lockout:
- **`COLLECT_EVIDENCE`**: Extracts historical logs and correlation context from database tables.
- **`LOOKUP_INDICATOR`**: Matches source IP and domain indicators against local threat intelligence feeds.
- **`CREATE_INCIDENT`**: Automatically creates an Incident case ticket linked to correlation chains.
- **`LINK_CORRELATION`**: Links related security alerts under a shared `CORR-YYYYMMDD-XXXX` ID.
- **`ADD_NOTE`**: Appends analyst investigation notes to incident history.
- **`UPDATE_STATUS`**: Updates alert status (`NEW` $\rightarrow$ `INVESTIGATING` $\rightarrow$ `RESOLVED`).
- **`REQUEST_ANALYST_APPROVAL`**: Pauses execution until an authorized analyst explicitly approves.
- **`GENERATE_AI_SUMMARY`**: Generates grounded 10-point AI Copilot triage summaries.
- **`SIMULATE_BLOCK_IP`**: Executes in **Lab Simulation Mode** (`SIMULATED ACTION: Would block IP x.x.x.x`). Never modifies live firewall or network rules.

---

## 3. Human Approval Workflow & Idempotency

- **Analyst Approval Control**: Potentially disruptive actions (such as IP containment) pause at state `PENDING_APPROVAL` until approved via `POST /api/v1/playbooks/approve`.
- **Idempotency**: Submitting duplicate execution requests for the same playbook and alert returns the existing execution ID without creating duplicate tickets or duplicate actions.

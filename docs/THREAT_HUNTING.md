# Threat Hunting & Safe Query Engine Architecture

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Proactive Threat Hunting Workspace, Natural Language Search, & Case Linking  

---

## 1. Threat Hunting Architecture Flow

```
[ Raw Security Telemetry ]
           ↓
[ Proactive Threat Hunting Workspace ]
           ↓
[ Safe Query Validation (Rejects Raw SQL / Injection Patterns) ]
           ↓
[ Parameterized SQLAlchemy ORM Execution ]
           ↓
[ Filtered Telemetry Results (Paginated) ]
           ↓
[ Entity / IOC Pivot → Threat Intel & ATT&CK Mapping ]
           ↓
[ Create / Link to Incident Case Ticket ]
```

---

## 2. AI Natural Language Translation & Grounding

- **Natural Language Translation**: Converts prompts such as *"Find repeated failed authentication attempts"* into safe ORM filters: `event_type=Authentication`, `search=failed login`, `severity=HIGH`.
- **Query Preview**: Displays generated parameters to analysts before executing searches.
- **Evidence Grounding**: AI summaries reference exact log event IDs (`#1`, `#2`). Returns `"INSUFFICIENT EVIDENCE"` when search results contain zero matches.

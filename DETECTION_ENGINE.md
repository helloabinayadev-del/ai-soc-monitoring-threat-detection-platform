# DETECTION_ENGINE.md - SIEM Threat Correlation Engine

## Overview

The SIEM Correlation Engine (`app/ai/threat_classifier.py`) evaluates ingested ECS log events against predefined security detection signatures and maps matches to MITRE ATT&CK tactical categories.

## Rule Signatures & MITRE ATT&CK Mapping

| Rule ID | Rule Name | Category | MITRE Tactic | MITRE Technique | Base Risk Score | Detection Pattern Keywords |
|---|---|---|---|---|---|---|
| `RULE-001` | Multiple Failed Logins (Brute Force) | Credential Access | `TA0006 - Credential Access` | `T1110 - Brute Force` | 75.0 | `failed login`, `invalid password`, `authentication failure` |
| `RULE-002` | Privilege Escalation via Sudo/Admin | Privilege Escalation | `TA0004 - Privilege Escalation` | `T1078 - Valid Accounts` | 90.0 | `sudo`, `administrator`, `runas`, `privilege escalation`, `root access` |
| `RULE-003` | Suspicious PowerShell Execution | Execution | `TA0002 - Execution` | `T1059.001 - PowerShell` | 85.0 | `powershell -enc`, `encodedcommand`, `downloadstring`, `iex` |
| `RULE-004` | Outbound Connection to Malicious C2 | Command & Control | `TA0011 - Command & Control` | `T1071 - Application Layer Protocol` | 95.0 | `c2 server`, `beacon`, `malicious ip`, `botnet connection` |
| `RULE-005` | Data Exfiltration over Encrypted Tunnel | Exfiltration | `TA0010 - Exfiltration` | `T1048 - Exfiltration Over Alternative Protocol` | 80.0 | `large payload`, `unusual port egress`, `dns tunneling` |
| `RULE-006` | SQL Injection (SQLi) Web Attack | Initial Access | `TA0001 - Initial Access` | `T1190 - Exploit Public-Facing Application` | 92.0 | `union select`, `' or 1=1`, `drop table`, `information_schema` |
| `RULE-007` | Ransomware File Encryption Activity | Impact | `TA0040 - Impact` | `T1486 - Data Encrypted for Impact` | 98.0 | `lockbit`, `encryptor`, `vssadmin delete shadows`, `malware execution` |

## Alert Correlation Workflow

```
Log Event Ingested ──► Rule Keyword Scan ──► Match Found? 
                            │                      │
                            ▼                      ▼
                   Run Anomaly Model      Generate SecurityAlert
                   Score > 65?            Set Risk Score & MITRE Code
                            │                      │
                            ▼                      ▼
                   Tag as ANOMALOUS ──────► Broadcast via WebSockets
```

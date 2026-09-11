from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class ThreatClassifier:
    def __init__(self):
        # Default MITRE ATT&CK Rule Patterns
        self.rules = [
            {
                "id": "RULE-001",
                "name": "Multiple Failed Logins (Brute Force)",
                "category": "Credential Access",
                "tactic": "TA0006 - Credential Access",
                "technique": "T1110 - Brute Force",
                "keywords": ["failed login", "invalid password", "authentication failure", "logon error"],
                "severity": "HIGH",
                "priority": "HIGH",
                "base_score": 75.0,
                "status": "ACTIVE",
                "version": 1,
                "author": "system",
                "condition_field": "raw_message",
                "condition_operator": "contains",
                "condition_value": "failed login"
            },
            {
                "id": "RULE-002",
                "name": "Privilege Escalation via Sudo/Admin",
                "category": "Privilege Escalation",
                "tactic": "TA0004 - Privilege Escalation",
                "technique": "T1078 - Valid Accounts",
                "keywords": ["sudo", "administrator", "runas", "privilege escalation", "root access"],
                "severity": "CRITICAL",
                "priority": "CRITICAL",
                "base_score": 90.0,
                "status": "ACTIVE",
                "version": 1,
                "author": "system",
                "condition_field": "raw_message",
                "condition_operator": "contains",
                "condition_value": "sudo"
            },
            {
                "id": "RULE-003",
                "name": "Suspicious PowerShell Command Execution",
                "category": "Execution",
                "tactic": "TA0002 - Execution",
                "technique": "T1059.001 - PowerShell",
                "keywords": ["powershell -enc", "encodedcommand", "downloadstring", "iex", "bypass"],
                "severity": "HIGH",
                "priority": "HIGH",
                "base_score": 85.0,
                "status": "ACTIVE",
                "version": 1,
                "author": "system",
                "condition_field": "raw_message",
                "condition_operator": "contains",
                "condition_value": "encodedcommand"
            },
            {
                "id": "RULE-004",
                "name": "Outbound Connection to Known Malicious C2",
                "category": "Command and Control",
                "tactic": "TA0011 - Command and Control",
                "technique": "T1071 - Application Layer Protocol",
                "keywords": ["c2 server", "beacon", "malicious ip", "botnet connection"],
                "severity": "CRITICAL",
                "priority": "CRITICAL",
                "base_score": 95.0,
                "status": "ACTIVE",
                "version": 1,
                "author": "system",
                "condition_field": "raw_message",
                "condition_operator": "contains",
                "condition_value": "c2 server"
            },
            {
                "id": "RULE-005",
                "name": "Potential Data Exfiltration over Encrypted Tunnel",
                "category": "Exfiltration",
                "tactic": "TA0010 - Exfiltration",
                "technique": "T1048 - Exfiltration Over Alternative Protocol",
                "keywords": ["large payload", "unusual port egress", "dns tunneling", "exfiltration"],
                "severity": "HIGH",
                "priority": "HIGH",
                "base_score": 80.0,
                "status": "ACTIVE",
                "version": 1,
                "author": "system",
                "condition_field": "raw_message",
                "condition_operator": "contains",
                "condition_value": "exfiltration"
            },
            {
                "id": "RULE-006",
                "name": "SQL Injection (SQLi) Web Application Attack",
                "category": "Initial Access / Injection",
                "tactic": "TA0001 - Initial Access",
                "technique": "T1190 - Exploit Public-Facing Application",
                "keywords": ["union select", "' or 1=1", "drop table", "information_schema", "sqli", "xp_cmdshell"],
                "severity": "CRITICAL",
                "priority": "CRITICAL",
                "base_score": 92.0,
                "status": "ACTIVE",
                "version": 1,
                "author": "system",
                "condition_field": "raw_message",
                "condition_operator": "contains",
                "condition_value": "union select"
            },
            {
                "id": "RULE-007",
                "name": "Ransomware / Malware File Encryption Activity",
                "category": "Impact",
                "tactic": "TA0040 - Impact",
                "technique": "T1486 - Data Encrypted for Impact",
                "keywords": ["lockbit", "encryptor", "vssadmin delete shadows", "readme.txt ransom", "malware execution"],
                "severity": "CRITICAL",
                "priority": "CRITICAL",
                "base_score": 98.0,
                "status": "ACTIVE",
                "version": 1,
                "author": "system",
                "condition_field": "raw_message",
                "condition_operator": "contains",
                "condition_value": "lockbit"
            }
        ]

    def classify_log(self, raw_message: str, parsed_fields: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        msg_lower = raw_message.lower()
        for rule in self.rules:
            if rule.get("status", "ACTIVE") != "ACTIVE":
                continue
            for kw in rule.get("keywords", []):
                if kw.lower() in msg_lower:
                    return {
                        "rule_id": rule["id"],
                        "rule_name": rule["name"],
                        "title": rule["name"],
                        "rule_version": rule.get("version", 1),
                        "category": rule["category"],
                        "mitre_tactic": rule.get("tactic", "TA0007 - Discovery"),
                        "mitre_technique": rule.get("technique", "T1082 - System Information Discovery"),
                        "severity": rule["severity"],
                        "priority": rule.get("priority", rule["severity"]),
                        "risk_score": rule.get("base_score", 75.0),
                        "matched_keyword": kw,
                        "explanation": f"Matched Rule {rule['id']} (v{rule.get('version', 1)}): Keyword '{kw}' found in raw log payload."
                    }
        return None

    def validate_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate rule parameters safely without executing unsafe code."""
        errors = []
        name = rule_data.get("name")
        if not name or len(name.strip()) < 3:
            errors.append("Rule name must be at least 3 characters long.")

        severity = rule_data.get("severity")
        if severity not in ["INFORMATIONAL", "LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            errors.append("Invalid severity level.")

        cond_operator = rule_data.get("condition_operator", "contains")
        if cond_operator not in ["equals", "contains", "starts_with", "ends_with", "greater_than", "less_than"]:
            errors.append("Invalid condition operator.")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def test_rule(self, rule_data: Dict[str, Any], test_log: Dict[str, Any]) -> Dict[str, Any]:
        """Test rule against arbitrary log payload returning MATCH or NO_MATCH."""
        validation = self.validate_rule(rule_data)
        if not validation["valid"]:
            return {"result": "ERROR", "message": "Rule validation failed", "errors": validation["errors"]}

        cond_field = rule_data.get("condition_field", "raw_message")
        cond_operator = rule_data.get("condition_operator", "contains")
        cond_val = str(rule_data.get("condition_value", "")).lower()

        log_val = str(test_log.get(cond_field, test_log.get("raw_message", ""))).lower()

        matched = False
        if cond_operator == "contains":
            matched = cond_val in log_val
        elif cond_operator == "equals":
            matched = cond_val == log_val
        elif cond_operator == "starts_with":
            matched = log_val.startswith(cond_val)
        elif cond_operator == "ends_with":
            matched = log_val.endswith(cond_val)

        return {
            "result": "MATCH" if matched else "NO_MATCH",
            "rule_id": rule_data.get("id", "TEST-RULE"),
            "tested_log": test_log.get("raw_message", "")[:100],
            "explanation": f"Condition ({cond_field} {cond_operator} '{cond_val}') evaluated to {matched} against test log."
        }

    def add_or_update_rule(self, rule_data: Dict[str, Any], author: str = "analyst") -> Dict[str, Any]:
        val = self.validate_rule(rule_data)
        if not val["valid"]:
            raise ValueError(f"Rule validation failed: {', '.join(val['errors'])}")

        rule_id = rule_data.get("id") or f"RULE-{len(self.rules) + 1:03d}"
        existing = next((r for r in self.rules if r["id"] == rule_id), None)

        if existing:
            existing["name"] = rule_data.get("name", existing["name"])
            existing["severity"] = rule_data.get("severity", existing["severity"])
            existing["priority"] = rule_data.get("priority", existing.get("priority", existing["severity"]))
            existing["status"] = rule_data.get("status", existing["status"])
            existing["condition_field"] = rule_data.get("condition_field", existing.get("condition_field", "raw_message"))
            existing["condition_operator"] = rule_data.get("condition_operator", existing.get("condition_operator", "contains"))
            existing["condition_value"] = rule_data.get("condition_value", existing.get("condition_value", ""))
            if rule_data.get("condition_value"):
                existing["keywords"] = [rule_data.get("condition_value")]
            existing["version"] = existing.get("version", 1) + 1
            existing["author"] = author
            existing["updated_at"] = datetime.now(timezone.utc).isoformat()
            return existing
        else:
            new_rule = {
                "id": rule_id,
                "name": rule_data["name"],
                "category": rule_data.get("category", "Custom Detection"),
                "tactic": rule_data.get("tactic", "TA0007 - Discovery"),
                "technique": rule_data.get("technique", "T1082 - System Information Discovery"),
                "keywords": [rule_data.get("condition_value", "suspicious")] if rule_data.get("condition_value") else ["suspicious"],
                "severity": rule_data.get("severity", "MEDIUM"),
                "priority": rule_data.get("priority", "MEDIUM"),
                "base_score": rule_data.get("base_score", 70.0),
                "status": rule_data.get("status", "ACTIVE"),
                "version": 1,
                "author": author,
                "condition_field": rule_data.get("condition_field", "raw_message"),
                "condition_operator": rule_data.get("condition_operator", "contains"),
                "condition_value": rule_data.get("condition_value", "")
            }
            self.rules.append(new_rule)
            return new_rule

threat_classifier = ThreatClassifier()

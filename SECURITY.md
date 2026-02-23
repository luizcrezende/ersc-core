# 🔐 ERSC Core — Security Policy

ERSC Core is an enterprise-grade federated AI governance engine designed for critical industrial environments.  
Security, auditability, and controlled autonomy are foundational principles of this architecture.

---

## 🛡 Supported Versions

This project is currently in active MVP development for AI Dev Days Hackathon.

| Version | Supported |
|----------|------------|
| 0.1.x (MVP) | ✅ Yes |
| < 0.1.0 | ❌ No |

Security updates will be applied to the latest active version only.

---

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability, please **do not open a public issue**.

Instead:

1. Send a detailed report via GitHub private security advisory (if enabled), or  
2. Contact the maintainer directly via LinkedIn or GitHub profile.

Please include:

- Description of the vulnerability  
- Steps to reproduce  
- Impact assessment  
- Suggested remediation (if available)

---

## 🔒 Security Principles

ERSC Core enforces:

- Policy-based AI execution control
- Risk scoring before execution
- Human-in-the-loop approval for critical actions
- Immutable audit logging
- Secure tool orchestration (Azure MCP-ready design)
- Azure-native deployment alignment

No AI-generated action should execute in production without:
- Policy validation
- Risk assessment
- Explicit authorization (when required)

---

## 🏗 Responsible AI Commitment

ERSC Core follows responsible AI and enterprise governance principles:

- Deterministic PLC layer separation
- Supervised autonomy
- Full traceability
- Secure-by-design architecture
- Compliance-ready structure

---

## 🔐 Dependency Management

Dependencies must:

- Be reviewed before addition
- Avoid known CVEs
- Follow minimal-attack-surface principles

Future roadmap includes:

- Automated dependency scanning
- CI security checks
- Static code analysis
- Container security validation

---

## 📌 Scope Disclaimer

This repository currently provides:

- Architectural demonstration
- MVP logic
- Governance simulation

It does **not** provide production industrial control code.

---

## 👤 Maintainer

Luiz Carlos Rezende da Silva  
Industrial Electrical Maintenance & AI Governance Architecture  
São Paulo, Brazil

---

Security is not an add-on.  
It is the architecture.

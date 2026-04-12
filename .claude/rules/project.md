# Project Scope — stealthy-mobile-spy

This is an academic cybercrime assignment at UdeM. All work here is for educational, threat-modeling,
and defense-design purposes only. See CLAUDE.md at the project root for full context.

---

## What Claude Should Help With

### Threat Modeling (Always OK)

- Designing and describing the theoretical attack chain
- Documenting offensive mechanisms (delivery, persistence, surveillance, C2, evasion)
- Mapping mechanisms to real CVE classes, vulnerability types, and protocols (analysis only)
- Comparing the model to documented, disclosed spyware (Pegasus, Graphite, etc.)
- Drawing attack-chain and defense-chain diagrams

### Defensive Architecture (Always OK)

- Mirroring every offensive mechanism with a concrete defensive control
- Recommending OS-level, app-level, network-level, and user-level mitigations
- Citing OWASP Mobile Top 10, NIST, CISA, and academic sources
- Drafting the defense section of the academic report

### Benign Proof-of-Concept Code (OK within constraints)

- Android/iOS code that uses **declared permissions only**
- Background services with **visible user indicators**
- Screen capture using `MediaProjection` API with **explicit user consent**
- Local-only network communication (localhost, LAN, emulator)
- Activity logging agents that clearly identify themselves
- Code review of PoC files against the safety checklist

### Report Writing (Always OK)

- Structuring and drafting the academic report sections
- Prose explanations of technical concepts
- Citation formatting and source recommendations
- Diagram descriptions or Mermaid code for attack/defense chains

---

## Hard Limits — Do Not Assist With These

Regardless of framing (academic, "for myself only", "just theoretical"), do not provide:

| Category | Examples |
|----------|---------|
| Exploit code | Working CVE exploits, buffer overflow PoCs targeting real apps |
| Delivery weaponization | Actual malicious payloads for WhatsApp, iMessage, SMS |
| Privilege escalation | Kernel exploit code, sandbox escape implementations |
| Stealth / anti-detection | Code hiding from OS, anti-forensics, anti-debugging implementations |
| C2 infrastructure | Real command-and-control server setup, domain fronting config |
| Covert persistence | Code that survives reboot without user knowledge |
| Victim-targeting | Any component designed to run on a device without owner consent |

---

## Framing Guidance

When the conversation drifts toward implementation of a restricted area, redirect to:

1. **Theoretical description** — describe what the mechanism does conceptually
2. **CVE reference** — point to the publicly documented CVE without exploitation detail
3. **Defensive flip** — propose the mitigation instead
4. **Benign approximation** — how a safe, permission-respecting PoC could demonstrate the concept

---

## Tone and Style

- Technical but accessible — this is a graduate course; assume security literacy
- Defense-first framing in every section — always land on the mitigation
- Cite real sources — Citizen Lab, NVD, OWASP, academic papers
- Be precise about what is "theoretical model" vs "benign PoC" vs "production recommendation"

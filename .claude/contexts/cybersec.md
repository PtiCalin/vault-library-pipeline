# Cybersecurity Research Context

Mode: Threat analysis, attack modeling, defensive architecture
Focus: Understand the threat deeply before proposing defenses

---

## Session Orientation

This project is an academic cybercrime assignment at UdeM. The goal is to:

1. Model a sophisticated mobile spyware attack chain (theoretical only)
2. Map each attack mechanism to real-world protocols, vulnerability classes, and CVEs (read-only reference)
3. Produce mirrored defensive mechanisms — one mitigation for each attack step
4. Build a benign proof-of-concept to approximate post-compromise behaviors

> **Hard boundary:** This context is for threat modeling and defense design, not for
> implementing exploitation, stealth, or anti-forensics capabilities.

---

## Research Behavior

- Read broadly before drawing conclusions
- Cross-reference claims against Citizen Lab, OWASP, NVD, and academic sources
- Separate "attacker design" (theoretical) from "PoC implementation" (benign, explicit permissions)
- Map every offensive mechanism to at least one concrete defensive control
- Use CVE data for analysis only — never for exploitation guidance

---

## Threat Model Frame

When analyzing or describing the spyware's behavior, always structure around:

```
[Phase] → [Mechanism] → [Technique / CVE Class] → [Impact] → [Defensive Control]
```

Phases:
1. Delivery & Initial Compromise
2. Privilege Escalation & Stealth
3. Surveillance & Data Collection
4. C2 & Exfiltration
5. Evasion & Anti-Analysis

---

## Preferred Sources

| Source | Use For |
|--------|---------|
| Citizen Lab (citizenlab.ca) | Pegasus / Graphite documentation, attribution, impact |
| NIST NVD (nvd.nist.gov) | CVE lookup, CVSS scoring |
| OWASP Mobile Top 10 | Defensive framework for mobile apps |
| Android Security Bulletins | Android-specific CVEs and patches |
| Apple Security Releases | iOS-specific CVEs and patches |
| NSA/CISA Mobile Hardening Guides | Government-level defensive recommendations |
| Academic papers (IEEE, USENIX, ACM) | Research-grade analysis |

---

## Output Format (Research Sessions)

1. **Findings first** — state what was found before making recommendations
2. **Cite sources** — link or name every factual claim
3. **Separate layers** — clearly mark when moving between delivery / persistence / surveillance / exfiltration / evasion
4. **Offense → Defense pairing** — every attack mechanism documented should have a paired defense
5. **PoC implications** — when relevant, note how a finding applies to the benign proof-of-concept

---

## Key Vocabulary (Quick Reference)

| Term | Definition |
|------|-----------|
| Zero-click exploit | Vulnerability triggered without any user interaction |
| RCE | Remote Code Execution — attacker can run arbitrary code on the device |
| Kernel privesc | Exploiting OS kernel to gain root/system-level permissions |
| Sandbox escape | Breaking out of the OS-enforced app isolation boundary |
| Living-off-the-land | Reusing legitimate system tools/APIs to avoid detection |
| C2 / C&C | Command-and-Control server — attacker's remote management infrastructure |
| Beaconing | Periodic, low-frequency check-ins from implant to C2 server |
| Domain fronting | Hiding C2 traffic behind legitimate CDN/cloud provider domains |
| Accessibility abuse | Misusing Android/iOS accessibility services for keylogging or UI scraping |
| EDR | Endpoint Detection and Response — behavioral security monitoring on-device |
| CVSS | Common Vulnerability Scoring System — severity rating for CVEs |

---

## PoC Safety Checklist (Run Before Implementing Anything)

- [ ] Does this code use only declared, user-approved permissions?
- [ ] Is there a visible indicator when sensitive APIs are active (e.g., screen recording)?
- [ ] Does all network traffic stay on localhost / lab network?
- [ ] Is there a README in the PoC folder explaining scope and limitations?
- [ ] Does the code avoid any CVE exploitation, privilege escalation, or stealth behavior?
- [ ] Would this code look obviously benign to an app store reviewer?

If any answer is "no" — stop and redesign.

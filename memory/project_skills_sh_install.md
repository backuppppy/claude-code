---
name: project-skills-sh-install
description: התקנו סקילים מ-skills.sh — בסיס (vercel/anthropic) + חבילת סייבר/תכנות/סריקה נבחרת
metadata: 
  node_type: memory
  type: project
  originSessionId: 7349132e-249a-4968-bd43-d4f40f48e4ca
---

המשתמש גילה את skills.sh (מאגר Agent Skills של Vercel; התקנה ב-`npx skills add <owner/repo> -s <skill> -g -y -a claude-code`).

**הותקנו גלובלית ב-`~/.claude/skills/` (25 סה"כ):**

סבב 1 (כללי): find-skills, frontend-design, vercel-react-best-practices, web-design-guidelines, agent-browser.

סבב 2 (חבילת סייבר/תכנות/סריקה נבחרת — 2026-06-11):
- התקפי (yaklang/hack-skills): sqli-sql-injection, xss-cross-site-scripting, ssrf-server-side-request-forgery, recon-and-methodology, android-pentesting-tricks, linux-privilege-escalation
- סריקה+פורנזיקה (mukul975/anthropic-cybersecurity-skills): scanning-network-with-nmap-advanced, performing-web-application-scanning-with-nikto, performing-vulnerability-scanning-with-nessus, performing-subdomain-enumeration-with-subfinder, analyzing-network-traffic-with-wireshark, analyzing-indicators-of-compromise, performing-memory-forensics-with-volatility3, performing-malware-triage-with-yara
- תכנות (wshobson/agents + נוספים): python-design-patterns, python-testing-patterns, python-error-handling, debugging-strategies, obra/superpowers@systematic-debugging, anthropics/skills@webapp-testing

**הקשר/החלטות:**
- בחר במודע "חבילה נבחרת" ולא "הכל", כי כל סקיל מותקן מנפח את ההקשר בכל שיחה. מאגרי הסייבר ענקיים: mukul975=754, yaklang=101, wshobson=156.
- סקילי הסייבר דורשים כלים חיצוניים (nmap/nikto/volatility/yara) — לבדוק זמינות ב-Termux לכל כלי בעת שימוש.
- שימוש מיועד ללמידה ובדיקות מורשות בלבד. **המשתמש אישר מפורשות (2026-06-12) שעבודת הסייבר היא על המעבדה שלו — סביבה בבעלותו עם הרשאה מלאה.** לזכור זאת בהמשך.
- מאגרים נוספים לבחירה עתידית: trailofbits/skills (סורקי פגיעויות בלוקצ'יין), aradotso/security-skills, mukul975 (עוד מאות סקילי blue-team/forensics).

קשור ל-[[user-environment]] (Termux/Android) ו-[[feedback-save-everything]].

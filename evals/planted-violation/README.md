# Planted-violation fixture

`BadProcessor.java` contains a deliberate §7 breach: a synchronous DB call inside a processor. Dispatch
the code reviewer (`claude/skills/sdd-dev/code-reviewer-prompt.md`) against it and assert it flags the
blocking I/O at **Blocker** and returns `changes-requested`. If it approves, the reviewer prompt regressed.

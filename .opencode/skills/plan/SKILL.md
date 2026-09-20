---
name: plan
description: Plan a feature by gathering requirements, asking clarifying questions, and outlining implementation
license: MIT
metadata:
  audience: developers
---

# Feature Planning

## When to use

Use this skill when asked to plan a new feature, design a system, or outline implementation steps before writing code.

## Process

### 1. Understand the request
- Identify goals, constraints, and the user's environment.
- Ask clarifying questions — at minimum about:
  - **Scope**: What exactly should the feature do? What is explicitly out of scope?
  - **Existing code**: Where should this integrate? Any relevant files/modules?
  - **Dependencies**: Any libraries, frameworks, or services to use or avoid?
  - **Edge cases**: Error states, empty states, concurrency concerns.
  - **Performance**: Any latency, memory, or throughput requirements?

### 2. Propose an approach
- Compare alternatives briefly if more than one reasonable path exists.
- Explain the trade-offs in 1-2 sentences per option.
- Give a clear recommendation.

### 3. Break down into steps
- Produce a numbered implementation plan with each step ordered by dependency.
- Each step should be independently testable where possible.
- Flag risky or ambiguous steps that may need revisiting.

### 4. Write the plan to a file
- Save the plan as a `.md` file in `./.opencode/plans/`.
- Use a descriptive filename based on the feature name (e.g., `dark-mode-toggle.md`).

### 5. Confirm before coding
- Wait for user sign-off before writing any implementation code.
- The plan itself should only produce the outline, not the implementation.

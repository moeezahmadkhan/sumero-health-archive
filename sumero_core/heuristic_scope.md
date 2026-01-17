# Heuristic Engine Constitution (Scope)

## 1. Sole Authority
The Heuristic Engine is the **sole authority** for health decisions in the Sumero Health platform.
All decisions regarding readiness, recovery state, and intervention timing originate here.

## 2. Deterministic Nature
The engine relies on **rigid, rule-based logic**.
- Inputs A + B must ALWAYS equal Decision C.
- No randomness allowed.

## 3. No AI Interference
Artificial Intelligence (LLMs, Neural Networks) is strictly **forbidden** from:
- Modifying the decision output.
- Inferring or guessing health states.
- Overriding safety protocols (e.g., "Stop Work" commands).

## 4. Controlled Language (Templates)
User-facing advice must be generated using **deterministic templates** and **controlled language blocks**.
- No LLM is allowed to generate health advice from scratch.
- The AI layer's scope is strictly **frozen** to: *Formatting, Tone Polishing, and UI presentation*.
- The *content* of the advice must be 100% trace-able to a specific heuristic rule.

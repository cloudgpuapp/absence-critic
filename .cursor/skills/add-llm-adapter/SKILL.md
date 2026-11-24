---
name: add-llm-adapter
description: Scaffold an LLM adapter that implements GeneratorPort and CriticPort without editing WaldLoop. Use when adding a provider, OpenAI-compatible backend, local model, or fixture LLM.
---

# Add LLM adapter

1. Implement both ports in `src/absencecritic/adapters/llm/` with **separate** methods: `generate`, `critique`, `revise`.
2. Load prompt text from `src/absencecritic/prompts/`. Do not inline a mega-prompt.
3. `generate` / `revise` must not take store hits. `critique` receives formatted store hits only.
4. Wire the name in `src/absencecritic/adapters/cli/main.py` (`--provider`) if it should be user-selectable. Local Ollama is `OpenAICompat.ollama()`, not a second HTTP stack.
5. Do not edit `application/loop.py` unless a port signature must change.
6. Tests: fixture-first. Live HTTP only when the user asked.
7. SPDX header. No LangChain/LangGraph/DSPy.

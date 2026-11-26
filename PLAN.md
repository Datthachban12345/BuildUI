# Plan: Improve Generated UI Design Quality

## Context
The reported storefront renders valid CSS but still looks generic: the model output/fallback is structurally valid yet lacks art direction, visual hierarchy, and meaningful media/CTA composition. Tailwind availability is no longer the primary issue. The workspace already contains concurrent changes to the A2UI adapter, generator, prompt, and renderer; implementation must build on the current on-disk state and avoid reverting unrelated/user edits.

## Recommended approach
1. **Map invalid model vocabulary instead of discarding design nodes.** Complete the current component-alias normalizer in `backend/app/agent/model_adapters/openrouter_adapter.py`; map common HTML/LLM names (`div`, `h1`, `img`, `ProductCard`, etc.) onto Astryx primitives while preserving useful props and children. Keep strict validation after normalization. Support `Image` in the validator, shared A2UI types, and renderer registry, completing the in-progress `AstryxImage` implementation in `frontend/src/catalog/adapters/astryx-adapter-view.tsx`.
2. **Raise the design contract from styling to composition.** Update `backend/app/agent/prompts/apple_designer.py` to require distinct art direction, a composed hero with real hierarchy and CTA, differentiated page sections, media slots when relevant, and richer commerce cards (image, category, price, action); discourage heading-plus-grid-only pages. Keep requirements compatible with the actual Astryx props/catalog and Tailwind safelist.
3. **Keep polish conservative and measurable.** Retain `backend/app/agent/generators/polish.py` as a missing-style-only pass; do not pretend spacing tokens can repair poor composition. Add a deterministic design-quality assessment in the generation pipeline that detects structural omissions (no visible content, no CTA/hero where appropriate, insufficient section hierarchy) and appends a targeted corrective turn rather than silently replacing the user's design with a generic hardcoded template. Ensure fallback behavior is transparent in SSE diagnostics.
4. **Make offline fallback domain-aware enough to avoid unrelated demos.** Update `backend/app/agent/generators/deterministic_payloads.py` only where needed so a failed model request does not show an unrelated Lumen/café page for a commerce prompt; preserve prompt-relevant brand/content and select an appropriate existing generation family. Do not add another universal branded template.
5. **Add regression tests.** Extend `tests/backend/test_phase3_harness.py` (and focused frontend tests if present) for alias preservation, `Image` rendering/catalog validity, quality-gate corrective retry, prompt composition constraints, and domain-consistent fallback. Test that already-designed LLM nodes remain unchanged by polish.

## Critical files
- `backend/app/agent/model_adapters/openrouter_adapter.py`
- `backend/app/agent/prompts/apple_designer.py`
- `backend/app/agent/generators/polish.py`
- `backend/app/agent/generators/a2ui_generator.py`
- `backend/app/agent/generators/deterministic_payloads.py`
- `backend/app/agent/validators/a2ui_validator.py`
- `frontend/src/a2ui/protocol/a2ui-types.ts`
- `frontend/src/catalog/adapters/astryx-adapter-view.tsx`
- `tests/backend/test_phase3_harness.py`

## Verification
- Run Python compile checks and the full backend test suite.
- Run the frontend TypeScript production build.
- Use deterministic mocked adapter responses to verify invalid component aliases retain visible content, quality failures trigger a corrective attempt, and fallback stays relevant to the user's prompt.
- Confirm no dev server is left running and inspect `git diff` to preserve unrelated workspace edits.

## Constraints
- Do not claim generative quality is solved by CSS safelisting or spacing polish alone.
- No fixed TechNova/Lumen template should overwrite valid model output.
- Preserve existing user/workspace modifications and report any test/build failures honestly.
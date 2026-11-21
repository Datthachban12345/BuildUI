import os
import sys
import json
import time
import asyncio
import httpx
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import Dict, Any, List, Optional, Tuple
from experiments.benchmark_qwen.evaluator.rubric import BenchmarkRubric
from backend.app.agent.validators.a2ui_validator import A2UIValidator

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Pricing per million tokens (OpenRouter approximate rates)
MODEL_PRICING = {
    "qwen/qwen-2.5-72b-instruct": {"input": 0.35, "output": 0.40},
    "qwen/qwen-2.5-coder-32b-instruct": {"input": 0.20, "output": 0.20},
    "openai/gpt-4o": {"input": 2.50, "output": 10.00},
    "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
}

A2UI_SYSTEM_PROMPT = """
You are an expert Frontend Architect specializing in the A2UI v1.0 protocol and Apple Design System.
Your job is to generate valid A2UI v1.0 JSON documents based on Astryx Component Catalog.

Allowed Astryx Components:
- Container, Row, Column, Grid
- Heading (props: level (1..4), text, className)
- Text (props: text, className)
- Button (props: label, variant ("primary"|"secondary"|"outline"|"ghost"), size ("sm"|"md"|"lg"))
- Card (props: title, description, className)
- Badge (props: label, variant)
- Input (props: placeholder, type, dataPath)
- MetricsCard (props: label, value, change, trend ("up"|"down"))
- DataTable (props: dataPath, searchable, pageSize, columns: [{key, title, sortable, type}])

Apple Design System Rules:
- Clean light mode: Pure white cards (bg-white), subtle borders (border-zinc-200), dark crisp text (text-zinc-950, text-zinc-600).
- Buttons: Primary buttons must be jet-black pill (bg-zinc-900 text-white rounded-full).

Envelope format:
{
  "version": "1.0",
  "createSurface": {
    "surfaceId": "page-main",
    "catalogId": "astryx-web-v1",
    "title": "Title",
    "components": [ ... ],
    "dataModel": { ... }
  }
}
Output strictly valid JSON only. No markdown fences.
"""

DESIGN_SPEC_PLANNER_PROMPT = """
You are an Elite Design Director at Apple. Given the user's website prompt, create a concise, high-taste Design Specification.
Outline:
1. Target Persona & Brand Vibe
2. Page Section Sequence (Header, Hero, Feature Grid, Pricing/Metrics, Contact, Footer)
3. Exact component mapping using Astryx Catalog
4. Micro-copy suggestions for Heading H1 and CTAs.
Keep the specification structured and concise under 300 words.
"""

class BenchmarkRunner:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")

    async def call_openrouter(
        self,
        model: str,
        messages: List[Dict[str, str]],
        json_mode: bool = True
    ) -> Tuple[Optional[str], float, int, int]:
        """
        Calls OpenRouter API, measures latency and token usage.
        """
        if not self.api_key:
            # Fallback mock for offline dry-run testing
            await asyncio.sleep(0.5)
            return '{"version": "1.0", "createSurface": {"surfaceId": "dry-run", "catalogId": "astryx-web-v1", "components": []}}', 0.5, 120, 350

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://buildui.local",
            "X-Title": "BuildUI A2UI Benchmark"
        }
        body: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": 0.5,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}

        start_time = time.time()
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(OPENROUTER_URL, headers=headers, json=body)
            latency = time.time() - start_time

            if res.status_code == 200:
                data = res.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                in_tokens = usage.get("prompt_tokens", 0)
                out_tokens = usage.get("completion_tokens", 0)
                return content, latency, in_tokens, out_tokens
            else:
                return None, latency, 0, 0

    def calculate_cost(self, model: str, in_tokens: int, out_tokens: int) -> float:
        rates = MODEL_PRICING.get(model, {"input": 1.0, "output": 2.0})
        cost = (in_tokens / 1_000_000) * rates["input"] + (out_tokens / 1_000_000) * rates["output"]
        return cost

    async def run_condition_1_pure_qwen(self, prompt: str) -> Dict[str, Any]:
        """Condition 1: Qwen designs and codes A2UI directly from raw prompt"""
        model = "qwen/qwen-2.5-72b-instruct"
        messages = [
            {"role": "system", "content": A2UI_SYSTEM_PROMPT},
            {"role": "user", "content": f"Design and generate website for: {prompt}"}
        ]
        raw_text, latency, in_tok, out_tok = await self.call_openrouter(model, messages, json_mode=True)
        cost = self.calculate_cost(model, in_tok, out_tok)

        parsed_json = None
        error = ""
        try:
            parsed_json = json.loads(raw_text or "{}")
            valid, err = A2UIValidator.validate_message(parsed_json)
            if not valid:
                error = err or "A2UI validation failed"
        except Exception as e:
            error = f"JSON parse error: {str(e)}"

        eval_res = BenchmarkRubric.evaluate_output(parsed_json, error, latency, cost, prompt)
        eval_res["model"] = model
        eval_res["condition"] = "Pure Qwen 72B"
        return eval_res

    async def run_condition_2_hybrid(self, prompt: str) -> Dict[str, Any]:
        """Condition 2: GPT-4o generates Design Spec -> Qwen 72B generates A2UI"""
        gpt_model = "openai/gpt-4o"
        qwen_model = "qwen/qwen-2.5-72b-instruct"

        # Step 1: GPT-4o Design Specification
        gpt_messages = [
            {"role": "system", "content": DESIGN_SPEC_PLANNER_PROMPT},
            {"role": "user", "content": f"Create Design Specification for: {prompt}"}
        ]
        spec_text, gpt_lat, gpt_in, gpt_out = await self.call_openrouter(gpt_model, gpt_messages, json_mode=False)
        gpt_cost = self.calculate_cost(gpt_model, gpt_in, gpt_out)

        # Step 2: Qwen generates A2UI based on GPT's Design Spec
        qwen_messages = [
            {"role": "system", "content": A2UI_SYSTEM_PROMPT},
            {"role": "user", "content": f"Prompt: {prompt}\n\nDesign Specification from Director:\n{spec_text}\n\nGenerate the complete A2UI v1.0 JSON according to this spec."}
        ]
        raw_json_text, qwen_lat, qwen_in, qwen_out = await self.call_openrouter(qwen_model, qwen_messages, json_mode=True)
        qwen_cost = self.calculate_cost(qwen_model, qwen_in, qwen_out)

        total_latency = gpt_lat + qwen_lat
        total_cost = gpt_cost + qwen_cost

        parsed_json = None
        error = ""
        try:
            parsed_json = json.loads(raw_json_text or "{}")
            valid, err = A2UIValidator.validate_message(parsed_json)
            if not valid:
                error = err or "A2UI validation failed"
        except Exception as e:
            error = f"JSON parse error: {str(e)}"

        eval_res = BenchmarkRubric.evaluate_output(parsed_json, error, total_latency, total_cost, prompt)
        eval_res["model"] = f"{gpt_model} + {qwen_model}"
        eval_res["condition"] = "Hybrid (GPT Spec -> Qwen A2UI)"
        eval_res["spec_preview"] = (spec_text[:120] + "...") if spec_text else ""
        return eval_res

    async def run_baseline_pure_gpt(self, prompt: str) -> Dict[str, Any]:
        """Baseline: GPT-4o alone designs and codes everything"""
        model = "openai/gpt-4o"
        messages = [
            {"role": "system", "content": A2UI_SYSTEM_PROMPT},
            {"role": "user", "content": f"Design and generate website for: {prompt}"}
        ]
        raw_text, latency, in_tok, out_tok = await self.call_openrouter(model, messages, json_mode=True)
        cost = self.calculate_cost(model, in_tok, out_tok)

        parsed_json = None
        error = ""
        try:
            parsed_json = json.loads(raw_text or "{}")
            valid, err = A2UIValidator.validate_message(parsed_json)
            if not valid:
                error = err or "A2UI validation failed"
        except Exception as e:
            error = f"JSON parse error: {str(e)}"

        eval_res = BenchmarkRubric.evaluate_output(parsed_json, error, latency, cost, prompt)
        eval_res["model"] = model
        eval_res["condition"] = "Baseline (Pure GPT-4o)"
        return eval_res

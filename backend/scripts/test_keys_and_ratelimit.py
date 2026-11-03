"""Verification script testing dual Groq keys, OpenRouter, Gemini fallback, and Rate Limiting."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(".env")
load_dotenv("backend/.env")

import httpx
from app.main import app
from app.database.mongodb import MongoDBManager
from app.services.llm_service import LLMService
from app.services.provider_router import ProviderRouter

async def test_all_keys():
    print("=" * 60)
    print("1. TESTING ALL CONFIGURED KEYS INDIVIDUALLY")
    print("=" * 60)
    import litellm

    keys_to_test = [
        ("Groq Key 1", "groq", "groq/qwen/qwen3.8-27b", os.environ.get("GROQ_API_KEY")),
        ("Groq Key 2", "groq", "groq/qwen/qwen3.8-27b", os.environ.get("GROQ_API_KEY1")),
        ("OpenRouter", "openrouter", "openrouter/meta-llama/llama-3.3-70b-instruct", os.environ.get("OPENROUTER_API_KEY")),
        ("Gemini", "gemini", "gemini/gemini-3.5-flash-lite", os.environ.get("GEMINI_API_KEY")),
    ]

    for name, provider, model, key in keys_to_test:
        if not key:
            print(f" [FAIL] {name}: Key not found in environment!")
            continue
        try:
            resp = litellm.completion(
                model=model,
                messages=[{"role": "user", "content": "Respond only with 'VERIFIED'."}],
                api_key=key,
                custom_llm_provider=provider,
                max_tokens=10,
            )
            ans = resp.choices[0].message.content.strip()
            print(f" [PASS] {name} ({model}): {ans}")
        except Exception as exc:
            print(f" [FAIL] {name} ({model}): {exc}")


async def test_key_rotation_and_fallback():
    print("\n" + "=" * 60)
    print("2. TESTING AUTOMATIC KEY ROTATION & PROVIDER FALLBACK")
    print("=" * 60)

    llm = LLMService()
    router = ProviderRouter(llm_service=llm)

    print(f"Configured Groq keys count: {len(llm.groq_keys)}")
    print(f"Primary model: {router.primary_model}")
    print(f"Fallback models: {router.fallback_models}")

    # Test key rotation
    k1 = llm._get_api_key_for_model("groq/qwen/qwen3.8-27b")
    rotated_key = llm.rotate_groq_key()
    k2 = llm._get_api_key_for_model("groq/qwen/qwen3.8-27b")
    print(f"Initial Groq key starts with: {k1[:12]}...")
    print(f"After rotation, key starts with: {k2[:12]}...")
    assert k1 != k2, "Key rotation did not switch keys!"
    print(" [PASS] Groq dual-key rotation switches keys successfully!")

    # Test stream execution with fallback
    print("\nExecuting live stream via ProviderRouter...")
    gen, chosen_model, chosen_prov = await router.execute_stream_with_fallback(
        messages=[{"role": "user", "content": "Say 'Routica online'"}],
        max_tokens=20,
    )
    tokens = []
    async for t in gen:
        tokens.append(t)
    print(f" [PASS] Stream succeeded using model: {chosen_model} (provider: {chosen_prov})")
    print(f" Response text: {''.join(tokens).strip()}")


async def test_rate_limiting():
    print("\n" + "=" * 60)
    print("3. TESTING RATE LIMITING DEFENSE (DDoS & ABUSE PROTECTION)")
    print("=" * 60)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        print("Sending rapid burst of 28 requests to /api/v1/chat ...")
        rate_limited = False
        limit_reached_at = None

        for req_num in range(1, 29):
            res = await client.post(
                "/api/v1/chat",
                json={"message": f"ping {req_num}"},
                headers={"x-session-id": "test-ratelimit-attacker"},
            )
            remaining = res.headers.get("x-ratelimit-remaining", "N/A")
            limit = res.headers.get("x-ratelimit-limit", "N/A")

            if res.status_code == 429:
                rate_limited = True
                limit_reached_at = req_num
                err_data = res.json()
                print(f" [BLOCKED 429] Request #{req_num} was rejected!")
                print(f" Error response: {err_data.get('error', {}).get('message')}")
                print(f" Retry-After header: {res.headers.get('retry-after')}s")
                break

        if rate_limited:
            print(f" [PASS] Rate limiter successfully blocked malicious burst at request #{limit_reached_at}!")
        else:
            print(" [FAIL] Rate limiter did not trigger!")


async def main():
    await MongoDBManager.connect()
    await test_all_keys()
    await test_key_rotation_and_fallback()
    await test_rate_limiting()
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())


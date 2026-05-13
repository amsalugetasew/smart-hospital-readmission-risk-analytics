import os
import sys

print("=" * 80)
print("CHECKING ENVIRONMENT VARIABLES DIRECTLY")
print("=" * 80)

# Check current directory
print(f"\nCurrent directory: {os.getcwd()}")

# Check if .env exists
env_path = os.path.join(os.getcwd(), '.env')
print(f".env path: {env_path}")
print(f".env exists: {os.path.exists(env_path)}")

# Try to read .env file directly
if os.path.exists(env_path):
    print("\n.env file contents (first 20 lines):")
    print("-" * 80)
    with open(env_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 20:
                break
            if 'GROQ_API_KEY' in line or 'LLM_PROVIDER' in line:
                print(f"Line {i+1}: {line.rstrip()}")
    print("-" * 80)

# Check environment variables BEFORE loading dotenv
print("\nEnvironment variables BEFORE dotenv:")
print(f"GROQ_API_KEY: {os.environ.get('GROQ_API_KEY', 'NOT SET')}")
print(f"LLM_PROVIDER: {os.environ.get('LLM_PROVIDER', 'NOT SET')}")

# Now load dotenv
print("\nLoading dotenv...")
try:
    from dotenv import load_dotenv
    result = load_dotenv(dotenv_path=env_path, override=True, verbose=True)
    print(f"load_dotenv result: {result}")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# Check environment variables AFTER loading dotenv
print("\nEnvironment variables AFTER dotenv:")
groq_key = os.environ.get('GROQ_API_KEY', '')
llm_provider = os.environ.get('LLM_PROVIDER', '')

print(f"GROQ_API_KEY: {groq_key[:30] if groq_key else 'NOT SET'}...")
print(f"GROQ_API_KEY length: {len(groq_key)}")
print(f"LLM_PROVIDER: {llm_provider}")

# Check using os.getenv (what the backend uses)
print("\nUsing os.getenv (what backend uses):")
groq_key2 = os.getenv('GROQ_API_KEY', '')
llm_provider2 = os.getenv('LLM_PROVIDER', '')

print(f"os.getenv('GROQ_API_KEY'): {groq_key2[:30] if groq_key2 else 'NOT SET'}...")
print(f"os.getenv('LLM_PROVIDER'): {llm_provider2}")

print("\n" + "=" * 80)
if groq_key and len(groq_key) > 20:
    print("✅ GROQ_API_KEY is loaded correctly!")
else:
    print("❌ GROQ_API_KEY is NOT loaded!")
print("=" * 80)

"""Quick test script to verify GROQ_API_KEY and GroqLLM connectivity."""
from llm.groq_llm import GroqLLM
from config.config import GROQ_API_KEY


def main():
    print("GROQ_API_KEY from config:", bool(GROQ_API_KEY))
    try:
        client = GroqLLM()
        print("GroqLLM instantiated successfully")
        resp = client.call("Say hello in one sentence.")
        print("Response:", resp)
    except Exception as e:
        print("Groq test failed:", str(e))


if __name__ == "__main__":
    main()
"""Quick test for Groq API key — runs a short prompt and prints the response."""
from llm.groq_llm import GroqLLM

def main():
    try:
        llm = GroqLLM()
        resp = llm.call("Say 'hello' and identify yourself in one short sentence.", temperature=0.0, max_tokens=50)
        print("GROQ call successful. Response:\n", resp)
    except Exception as e:
        print("GROQ test failed:", e)

if __name__ == '__main__':
    main()

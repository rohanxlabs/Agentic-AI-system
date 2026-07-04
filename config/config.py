"""Configuration module for the Agentic AI System."""
import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))

# System Configuration
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "5"))
SHORT_TERM_MEMORY_SIZE = int(os.getenv("SHORT_TERM_MEMORY_SIZE", "10"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/agentic_system.log")
MEMORY_FILE = os.getenv("MEMORY_FILE", "logs/memory.json")

# Timeouts and Limits
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "3"))

# Embeddings and Memory Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
MEMORY_TOP_K = int(os.getenv("MEMORY_TOP_K", "5"))

# Validation
if not GROQ_API_KEY:
    print("Warning: GROQ_API_KEY not set in environment variables")
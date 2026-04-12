# -*- coding: utf-8 -*-
import os
LLM_PROVIDER = os.getenv('llm_provider', 'groq').lower()
GROQ_API_KEY = os.getenv('groq_api_key', '')
GROQ_MODEL = os.getenv('groq_model', 'llama-3.3-70b-versatile')
OPENAI_API_KEY = os.getenv('openai_api_key', '')
OPENAI_BASE_URL = os.getenv('openai_base_url', 'https://api.openai.com/v1')
OPENAI_MODEL = os.getenv('openai_model', 'gpt-4o-mini')
HOST = os.getenv('host', '0.0.0.0')
PORT = int(os.getenv('port', '8001'))
DEBUG = os.getenv('debug', 'false').lower() == 'true'

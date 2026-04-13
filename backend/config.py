# -*- coding: utf-8 -*-
import os

LLM_PROVIDER = os.getenv('llm_provider', os.getenv('LLM_PROVIDER', 'groq')).lower()
GROQ_API_KEY = os.getenv('groq_api_key', os.getenv('GROQ_API_KEY', ''))
GROQ_MODEL = os.getenv('groq_model', os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile'))
OPENAI_API_KEY = os.getenv('openai_api_key', os.getenv('OPENAI_API_KEY', ''))
OPENAI_BASE_URL = os.getenv('openai_base_url', os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'))
OPENAI_MODEL = os.getenv('openai_model', os.getenv('OPENAI_MODEL', 'gpt-4o-mini'))
HOST = os.getenv('host', '0.0.0.0')
PORT = int(os.getenv('port', os.getenv('PORT', '8001')))
DEBUG = os.getenv('debug', 'false').lower() == 'true'

VOXTRAL_MODELS = ["voxtral-mini-latest", "voxtral-small-latest"]
MISTRAL_MODELS = ["mistral-small-latest", "mistral-medium-latest"]
MAGISTRAL_MODELS = ["magistral-small-latest", "magistral-medium-latest"]
GPT_5_MODELS = ["gpt-5-nano", "gpt-5-mini", "gpt-5.1"]
GPT_4_MODELS = ["gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano"]
TOGETHER_MODELS = ["deepseek-ai/DeepSeek-R1-0528-tput", "Qwen/Qwen3-235B-A22B-fp8-tput", "openai/gpt-oss-120b"]
O4_MODELS = ["o4-mini"]

IMAGE_CAPABLE_MODELS = MISTRAL_MODELS + MAGISTRAL_MODELS + GPT_5_MODELS + GPT_4_MODELS + O4_MODELS
THINKING_MODELS = TOGETHER_MODELS + MAGISTRAL_MODELS + GPT_5_MODELS + O4_MODELS
ALL_MODELS = VOXTRAL_MODELS + MISTRAL_MODELS + MAGISTRAL_MODELS + GPT_5_MODELS + GPT_4_MODELS + TOGETHER_MODELS + O4_MODELS

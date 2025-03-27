# Example LLM configurations - please use the template for your own specific LLM
import os
from langchain_openai import ChatOpenAI
from langchain_ollama.llms import OllamaLLM

available_llms = {
    "openai[gpt-4o-mini]": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "class": ChatOpenAI,
        "default_kwargs": {
            "temperature": 0.7,
            "model_kwargs": {
                "top_p": 1,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1,
            }
        },
    },
    "ollama[llama3:70b]": {
        "provider": "ollama",
        "model": "llama3:70b",
        "class": OllamaLLM,
        "default_kwargs": {
            "base_url": "http://localhost:11434",
            "temperature": 0.7,
            "top_p": 1,
            # Add any other default Ollama parameters here
        },
    },
    "ollama[openhermes]": {
        "provider": "ollama",
        "model": "openhermes",
        "class": OllamaLLM,
        "default_kwargs": {
            "base_url": "http://localhost:11434",
            "temperature": 0.7,
             "top_p": 1,
        },
    },
    "anthropic[claude-3-sonnet-20240229-v1:0]": {
        "provider": "anthropic",
        "model": "claude-3-sonnet-20240229-v1:0",
        "class": ChatOpenAI,  # Assuming you use ChatOpenAI for Anthropic
        "default_kwargs": {
            "temperature": 0.7,
             "top_p": 1,
             "model_kwargs": {}
        },
    },
     "google[gemini-1.5-pro-latest]": {
        "provider": "google",
        "model": "gemini-1.5-pro-latest",
        "class": ChatOpenAI,  # Assuming you use ChatOpenAI for Google
        "default_kwargs": {
            "temperature": 0.7,
            "top_p": 1,
            "model_kwargs": {},
            "vertex_credentials": "YOUR_VERTEX_CREDENTIALS_JSON" # Placeholder, see below

        },
    },
    # Add more LLMs here, following the same pattern
    "openai[gpt-4]": {
        "provider": "openai",
        "model": "gpt-4",
        "class": ChatOpenAI,
        "default_kwargs": {
            "temperature": 0.7,
            "model_kwargs": {
                "top_p": 1,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1,
            }
        },
    },
     "openai[gpt-3.5-turbo]": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "class": ChatOpenAI,
        "default_kwargs": {
            "temperature": 0.7,
            "model_kwargs": {
                "top_p": 1,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1,
            }
        },
    },
}

def get_llm(llm_choice, **kwargs):
    print(f"Attempting to create LLM instance for: {llm_choice}")  # Debug
    if llm_choice not in available_llms:
        raise ValueError(f"Invalid LLM choice: {llm_choice}")

    llm_config = available_llms[llm_choice]
    provider = llm_config["provider"]
    model_name = llm_config["model"]
    llm_class = llm_config["class"]
    default_kwargs = llm_config.get("default_kwargs", {})

    final_kwargs = default_kwargs.copy()
    final_kwargs.update(kwargs)

    try:
        if provider == "openai":
            instance = llm_class(model=model_name, openai_api_key=os.environ.get("OPENAI_API_KEY"), **final_kwargs)
        elif provider == "ollama":
            instance = llm_class(model=model_name, **final_kwargs)
        elif provider == "anthropic":
            instance = llm_class(model=model_name, openai_api_key=os.environ.get("ANTHROPIC_API_KEY"), **final_kwargs)
        elif provider == "google":
            instance = llm_class(model=model_name, openai_api_key=os.environ.get("GEMINI_API_KEY"), **final_kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        print(f"Successfully created LLM instance: {instance}")  # Debug
        return instance

    except Exception as e:
        print(f"Error creating LLM instance for {llm_choice}: {e}")  # Debug
        return None

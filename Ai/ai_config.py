import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("InterviewTrainer.AI")

IBM_CLOUD_API_KEY = os.getenv("IBM_CLOUD_API_KEY")
IBM_CLOUD_URL = os.getenv("IBM_CLOUD_URL", "https://us-south.ml.cloud.ibm.com")
PROJECT_ID = os.getenv("PROJECT_ID")

def get_watsonx_model(max_tokens: int = 1500, temperature: float = 0.7):
    """Initializes and returns IBM Watsonx ModelInference instance if credentials exist."""
    if not IBM_CLOUD_API_KEY or not PROJECT_ID:
        logger.warning("IBM Cloud credentials or PROJECT_ID missing. Operating in fallback mode.")
        return None

    try:
        from ibm_watsonx_ai.foundation_models import ModelInference
        credentials = {
            "url": IBM_CLOUD_URL,
            "apikey": IBM_CLOUD_API_KEY
        }
        parameters = {
            "decoding_method": "sample",
            "temperature": temperature,
            "max_new_tokens": max_tokens,
            "min_new_tokens": 1,
            "repetition_penalty": 1.1
        }
        model_id = "meta-llama/llama-3-3-70b-instruct"
        model = ModelInference(
            model_id=model_id,
            credentials=credentials,
            project_id=PROJECT_ID,
            params=parameters
        )
        return model
    except Exception as e:
        logger.error(f"Failed to initialize IBM Watsonx client: {e}")
        try:
            from ibm_watsonx_ai.foundation_models import ModelInference
            model = ModelInference(
                model_id="ibm/granite-13b-chat-v2",
                credentials=credentials,
                project_id=PROJECT_ID,
                params=parameters
            )
            return model
        except Exception as e2:
            logger.error(f"Granite fallback failed: {e2}")
            return None


def generate_text_watsonx(prompt: str, max_tokens: int = 1500) -> str:
    """Generate text using IBM Watsonx.ai Foundation Models with graceful error handling."""
    model = get_watsonx_model(max_tokens=max_tokens)
    if model:
        try:
            response = model.generate_text(prompt=prompt)
            if response and response.strip():
                return response.strip()
        except Exception as e:
            logger.error(f"Error during IBM Watsonx inference: {e}")

    return ""

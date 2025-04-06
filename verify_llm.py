import sys
import os

# Add the project directory to the Python path to find config
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

try:
    # Import necessary components
    from langchain_ollama import OllamaLLM as Ollama # Use OllamaLLM and alias it back to Ollama
    import config # Assuming config.py is in the same directory

    print("Imports successful.")

    # Attempt to initialize the LLM
    print(f"Attempting to initialize Ollama LLM with model '{config.OLLAMA_MODEL_NAME}' from '{config.OLLAMA_BASE_URL}'...")
    llm = Ollama(
        model=config.OLLAMA_MODEL_NAME,
        base_url=config.OLLAMA_BASE_URL
    )
    # Accessing an attribute to ensure the object is usable
    print(f"Ollama LLM object created. Model attribute: {llm.model}")
    print("\nVerification successful! The Ollama LLM can be initialized with the current setup.")
    sys.exit(0) # Explicitly exit with success code

except ImportError as e:
    print(f"\nVerification failed: Import Error - {e}")
    print("Please double-check that 'langchain-ollama' is installed correctly (`myenv/bin/pip show langchain-ollama`) and that the import statement in agents.py is correct.")
    sys.exit(1) # Exit with error code
except AttributeError as e:
     print(f"\nVerification failed: Attribute Error - {e}")
     print("This might indicate an issue with the 'config.py' file (e.g., missing OLLAMA_MODEL_NAME or OLLAMA_BASE_URL) or an incompatibility with the Ollama library version.")
     sys.exit(1) # Exit with error code
except Exception as e:
    print(f"\nVerification failed: An unexpected error occurred - {e}")
    print("This could be due to various reasons, including issues connecting to the Ollama service at the specified base URL.")
    sys.exit(1) # Exit with error code
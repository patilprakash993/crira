# CRIRA - Customer Review Insight & Response Automation

CRIRA is a Python-based LLM system that automates customer review analysis and generates empathetic, on-brand responses. It is built with a security-first mindset, ensuring robust PII redaction, defending against prompt injection attacks, and delivering a secure, scalable solution.

## Setup

1.  **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2.  **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3.  **Install the project in editable mode:**
   This makes the `crira` package available to your environment and resolves import paths.
   ```bash
   pip install -e .
   ```
3.  **Configure environment variables:**
    Create a `.env` file in the root directory of the project and add your Google API key.
    ```ini
    # .env file
    GOOGLE_API_KEY="your-google-api-key-here"
    ```
    The application supports the following environment variables:
    -   `CRIRA_SAFE_MODE` (default: `true`): Enables all security features like PII redaction and bracket escaping. Set to `false` to run in an unsafe demonstration mode.
    -   `CRIRA_USE_REAL_LLM` (default: `false`): Set to `true` to make live calls to the Gemini API. If `false`, a deterministic dummy LLM is used for offline testing.
    -   `GOOGLE_API_KEY`: Required if `CRIRA_USE_REAL_LLM=true`.
    -   `CRIRA_LLM_MODEL` (default: `gemini-1.5-flash-latest`): Allows you to specify a different Gemini model.

## How to Run

The application processes a JSON file of customer reviews and generates a corresponding results file.

1.  **Run with the dummy LLM (default, offline):**
    This command uses the dummy LLM client, which requires no API key and produces deterministic output.
    ```bash
    python -m crira.main --reviews reviews.json --output results.json
    ```

2.  **Run with the real Gemini LLM:**
    Set `CRIRA_USE_REAL_LLM=true` to connect to the Google Gemini API. Make sure your `GOOGLE_API_KEY` is set in the `.env` file.
    ```bash
    export CRIRA_USE_REAL_LLM=true
    python -m crira.main --reviews reviews.json --output results.json
    ```

## How to Test

The test suite is designed to run offline using the dummy LLM, ensuring that tests are fast, deterministic, and do not require an active internet connection or API keys.

To run the full test suite, execute `pytest` from the root directory:
```bash
pytest -v
```

The tests cover critical functionality, including:
-   PII redaction logic.
-   The critical review policy and `CRITICAL_REF` generation.
-   Defenses against common prompt injection attacks.

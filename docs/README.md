# CRIRA: Customer Review Insight and Response Automator

CRIRA is a Python-based application designed to automate the analysis of customer reviews and generate empathetic, on-brand responses. It leverages Large Language Models (LLMs) like Google's Gemini while prioritizing security through a multi-layered, defense-in-depth strategy.

## Project Structure

```
crira/
├── .github/workflows/      # CI/CD pipeline configuration
├── docs/                   # Project documentation (design, prompts)
├── src/                    # Core application source code
│   ├── analysis_engine.py  # PII redaction and LLM analysis logic
│   ├── response_generator.py # Response generation and security validation
│   ├── llm_client.py       # Client for real and dummy LLMs
│   ├── config.py           # Configuration loader
│   ├── prompts.py          # System and few-shot prompts
│   └── main.py             # CLI entry point
├── tests/                  # Pytest test suite
├── .gitignore
├── requirements.txt        # Python dependencies
└── reviews.json            # Example input data
```

## Core Features

-   **Automated Review Analysis**: Extracts sentiment (positive, negative, neutral), key issues or praise, and generates a concise summary for each review.
-   **Secure PII Redaction**: Automatically identifies and redacts Personally Identifiable Information (PII) like names, emails, and phone numbers before sending data to the LLM.
-   **AI-Powered Response Generation**: Creates professional and empathetic customer-facing responses tailored to the review's content.
-   **Critical Review Flagging**: Deterministically flags reviews containing urgent keywords (e.g., "ruined", "unacceptable") and appends a secure, backend-generated critical reference ID.
-   **Robust Security**: Built with strong defenses against prompt injection, data leakage, and other LLM vulnerabilities.
-   **Testable & Configurable**: Includes a full test suite and supports a dummy LLM for offline development, ensuring logic can be validated without API costs.

## Security by Design

CRIRA is built with a security-first mindset, implementing several layers of protection:

1.  **Input Sanitization & Redaction**:
    -   **PII Redaction**: Uses deterministic regex to remove sensitive data *before* it reaches the LLM.
    -   **Canonicalization**: Normalizes input text to remove obfuscated characters that could be used for injection attacks.
    -   **Bracket Escaping**: Escapes `[` and `]` characters to prevent attackers from mimicking system tokens.

2.  **Prompt Engineering**:
    -   System prompts contain explicit negative constraints, instructing the LLM to ignore user-led injection attempts.
    -   The LLM is assigned a clear role (e.g., `CustomerCareBot`) to maintain context and adhere to its designated task.

3.  **Backend Enforcement**:
    -   Critical business logic, like generating a `CRITICAL_REF` ID, is handled exclusively by the backend application code, never by the LLM.
    -   The application validates LLM output, stripping any hallucinated PII placeholders or forbidden tokens.

## Getting Started

### Prerequisites

-   Python 3.11+
-   Git

### 1. Clone the Repository

```bash
git clone https://github.com/patilprakash993/crira.git
cd crira
```

## Setup

### 2. Install Dependencies

It is recommended to use a virtual environment.

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 3. Configure Environment Variables

The application is configured via environment variables. You can set them in your shell or create a `.env` file (ensure `.env` is in your `.gitignore`).

**For Dummy LLM (Default, for testing):**

No API key is needed. The application runs in `SAFE_MODE` with the dummy LLM by default.
Either set enivronment variable or change in config.json.

```bash
# These are the default values, so setting them is optional for dummy mode
export CRIRA_SAFE_MODE="true"
export CRIRA_USE_REAL_LLM="false"
```

**For Real LLM (Google Gemini):**

To use the actual Gemini model, you need a Google AI Studio API key.
Either set enivronment variable or change in config.json.

```bash
export GOOGLE_API_KEY="your_google_api_key_here"
export CRIRA_USE_REAL_LLM="true"

# Optional: You can run the real LLM in UNSAFE_MODE to see the effect of security controls
# export CRIRA_SAFE_MODE="false"
```

## Security Modes Explained

-   **`SAFE_MODE=true` (Default & Recommended):**
    -   **PII Redaction**: Scrubs sensitive data (names, emails, etc.) before it is sent to the LLM.
    -   **Bracket Escaping**: Prevents attackers from injecting fake system tokens.
    -   This is the secure, production-ready configuration.

-   **`SAFE_MODE=false` (For Demonstration Only):**
    -   Disables PII redaction and other input sanitization steps.
    -   This mode is useful only to demonstrate the risks of running an LLM application without proper input security controls.


## Usage

The application processes a JSON file of customer reviews and generates a corresponding results file.

```bash
python src/main.py --reviews reviews.json --output my_results.json
```

-   `--reviews`: Path to the input JSON file (defaults to `reviews.json`).
-   `--output`: Path for the output results file (defaults to `results.json`).

The script will process each review in `reviews.json` and write the analysis and generated response to `my_results.json`.

## Running Tests & Linting

The project includes a comprehensive test suite using `pytest` and a linter (`Ruff`). The tests run offline using the dummy LLM and do not require an API key.

To run the full test suite:
```bash
pytest -v
```

The tests cover critical functionality, including:
-   PII redaction logic.
-   The critical review policy and `CRITICAL_REF` generation.
-   Defenses against common prompt injection attacks.

To check code formatting and quality:
```bash
ruff check .
ruff format --check .
```

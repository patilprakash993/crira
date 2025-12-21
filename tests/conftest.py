import os
import pytest

# By default tests run in SAFE mode using dummy LLM
os.environ["CRIRA_SAFE_MODE"] = "true"
os.environ["CRIRA_USE_REAL_LLM"] = "false"

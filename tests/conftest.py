"""Shared fixtures: ensure project root importable without paid LLM calls."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

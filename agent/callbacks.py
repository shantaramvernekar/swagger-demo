"""Callback handlers for streaming agent activity to the console."""
from __future__ import annotations

from typing import Any, Dict, Iterable, Optional
import sys
import threading

from langchain_core.agents import AgentAction
from langchain_core.callbacks import BaseCallbackHandler


class ConsoleCallbackHandler(BaseCallbackHandler):
    """Stream agent reasoning steps and tool usage to stdout in real time."""

    def __init__(self, stream: Optional[Any] = None) -> None:
        self.stream = stream or sys.stdout
        self._lock = threading.Lock()

    # Utility -----------------------------------------------------------------
    def _write(self, text: str) -> None:
        with self._lock:
            print(text, file=self.stream)
            self.stream.flush()

    def _render_lines(self, prefix: str, content: str) -> None:
        for line in content.strip().splitlines():
            self._write(f"{prefix}{line}")

    # LLM callbacks ------------------------------------------------------------
    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: Iterable[str],
        **kwargs: Any,
    ) -> None:
        for prompt in prompts:
            if prompt.strip():
                self._render_lines("[Prompt] ", prompt)

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        generations = getattr(response, "generations", None)
        if not generations:
            return
        for generation in generations:
            for item in generation:
                text = getattr(item, "text", "")
                if text:
                    self._render_lines("[LLM] ", text)

    # Agent callbacks ----------------------------------------------------------
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        if getattr(action, "log", None):
            self._render_lines("[Agent] ", str(action.log))
        tool_input = getattr(action, "tool_input", None)
        if tool_input is not None:
            self._render_lines(
                f"[Tool > {action.tool}] ",
                str(tool_input),
            )

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: Any,
        parent_run_id: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        tool_name = serialized.get("name") or serialized.get("id") or "tool"
        if input_str.strip():
            self._render_lines(f"[Tool > {tool_name}] ", input_str)

    def on_tool_end(self, output: Any, **kwargs: Any) -> None:
        if output is None:
            return
        self._render_lines("[Tool <] ", str(output))

    def on_text(self, text: str, **kwargs: Any) -> None:
        if text.strip():
            self._render_lines("[Agent] ", text)

    def on_agent_finish(self, finish: Any, **kwargs: Any) -> None:
        final_log = getattr(finish, "log", None)
        if final_log:
            self._render_lines("[Agent] ", str(final_log))

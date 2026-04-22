from __future__ import annotations

import hashlib
import os
import re
from typing import Iterable

from app.safety.types import ActionKind, PolicyDecision, SafetyCheckRequest, SafetyEvaluation


_READ_ONLY_COMMAND_PREFIXES = (
    "cat",
    "echo",
    "find",
    "git diff",
    "git log",
    "git show",
    "git status",
    "head",
    "ls",
    "pwd",
    "python -m unittest",
    "python3 -m unittest",
    "sed -n",
    "tail",
)

_MUTATING_COMMAND_MARKERS = (
    "pip install",
    "pip3 install",
    "poetry add",
    "npm install",
    "npm update",
    "apt-get",
    "brew install",
    "git reset --hard",
    "git checkout --",
    "git clean",
    "rm ",
    "mv ",
    "cp ",
    "chmod ",
    "chown ",
    "curl ",
    "wget ",
    "sh ",
    "bash ",
)

_DANGEROUS_FETCH_AND_EXECUTE_PATTERNS = (
    "curl ",
    "wget ",
)


def normalize_command(command: str | None) -> str:
    return " ".join(str(command or "").strip().lower().split())


def _normalized_path(path: str | None) -> str:
    if not path:
        return ""
    return os.path.abspath(path)


def _targets_repo_root(path: str | None, repo_root: str) -> bool:
    if not path:
        return False
    normalized = _normalized_path(path)
    repo_root = _normalized_path(repo_root)
    if not normalized or not repo_root:
        return False
    return normalized == repo_root or normalized.startswith(f"{repo_root}{os.sep}")


def action_fingerprint(request: SafetyCheckRequest) -> str:
    normalized = "|".join(
        [
            request.action_kind.value,
            str(request.action_name or "").strip().lower(),
            normalize_command(request.command),
            _normalized_path(request.target_path),
        ]
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _contains_any(text: str, markers: Iterable[str]) -> bool:
    return any(marker in text for marker in markers)


def _is_repo_delete_operation(request: SafetyCheckRequest, repo_root: str) -> bool:
    name = str(request.action_name or "").strip().lower()
    destructive_names = {"delete_repo", "delete repository", "remove_repository", "destroy_repo", "wipe_repo"}
    if name in destructive_names:
        return True
    return request.action_kind == ActionKind.REPO_OPERATION and _targets_repo_root(request.target_path, repo_root)


def _is_dangerous_shell_command(command: str, repo_root: str) -> tuple[bool, list[str]]:
    rules: list[str] = []
    repo_root_norm = _normalized_path(repo_root).lower()

    delete_patterns = [
        r"(^|\s)rm\s+-[A-Za-z-]*r[A-Za-z-]*f[A-Za-z-]*(\s+\.($|\s)|\s+/tmp/zero-human-sandbox($|\s))",
        r"(^|\s)git\s+clean\s+-fdx(\s|$)",
        r"(^|\s)rm\s+-[A-Za-z-]*r[A-Za-z-]*f[A-Za-z-]*\s+\.git(\s|$)",
    ]
    for pattern in delete_patterns:
        if re.search(pattern, command):
            rules.append("destructive_repo_command")

    if repo_root_norm and repo_root_norm in command and "rm " in command:
        rules.append("repo_root_targeted_delete")

    if any(fetch in command for fetch in _DANGEROUS_FETCH_AND_EXECUTE_PATTERNS) and ("| sh" in command or "| bash" in command):
        rules.append("remote_script_execution")

    if ".git" in command and _contains_any(command, ("rm ", "mv ", "cp ", "chmod ", "chown ")):
        rules.append("git_metadata_mutation")

    return (len(rules) > 0, rules)


def _requires_approval_shell_command(command: str) -> tuple[bool, list[str]]:
    rules: list[str] = []
    if _contains_any(command, _MUTATING_COMMAND_MARKERS):
        rules.append("mutating_shell_command")
    if any(token in command for token in ("&&", "||", ";", "|")) and rules:
        rules.append("compound_shell_command")
    if "git reset --hard" in command or "git checkout --" in command:
        rules.append("history_or_workspace_rewrite")
    return (len(rules) > 0, rules)


def evaluate_request(request: SafetyCheckRequest, repo_root: str) -> SafetyEvaluation:
    fingerprint = action_fingerprint(request)

    if _is_repo_delete_operation(request, repo_root):
        return SafetyEvaluation(
            decision=PolicyDecision.DENY,
            reason_code="repo_deletion_blocked",
            message="Repository deletion or destruction is blocked by policy.",
            matched_rules=["repo_delete_operation"],
            action_fingerprint=fingerprint,
        )

    if request.action_kind == ActionKind.SHELL_COMMAND:
        command = normalize_command(request.command)
        if not command:
            return SafetyEvaluation(
                decision=PolicyDecision.ALLOW,
                reason_code="empty_command",
                message="No shell command was provided.",
                action_fingerprint=fingerprint,
            )

        dangerous, dangerous_rules = _is_dangerous_shell_command(command, repo_root)
        if dangerous:
            return SafetyEvaluation(
                decision=PolicyDecision.DENY,
                reason_code="unsafe_command_blocked",
                message="Unsafe destructive shell command blocked by policy.",
                matched_rules=dangerous_rules,
                action_fingerprint=fingerprint,
            )

        if command.startswith(_READ_ONLY_COMMAND_PREFIXES):
            return SafetyEvaluation(
                decision=PolicyDecision.ALLOW,
                reason_code="read_only_command",
                message="Read-only shell command allowed.",
                action_fingerprint=fingerprint,
            )

        needs_approval, approval_rules = _requires_approval_shell_command(command)
        if needs_approval:
            return SafetyEvaluation(
                decision=PolicyDecision.REQUIRE_APPROVAL,
                reason_code="approval_required",
                message="This shell command requires explicit approval before execution.",
                matched_rules=approval_rules,
                action_fingerprint=fingerprint,
            )

    return SafetyEvaluation(
        decision=PolicyDecision.ALLOW,
        reason_code="allowed",
        message="Action allowed by current safety policy.",
        action_fingerprint=fingerprint,
    )

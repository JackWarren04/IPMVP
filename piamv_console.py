#!/usr/bin/env python3
"""Console for running PIAM&V projects."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List


DATA_DIR = Path("data/projects")


@dataclass
class Rule:
    source: str
    title: str
    text: str
    section: str = ""
    page: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class SourceDocument:
    name: str
    path: str
    notes: str = ""
    added_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ProjectStep:
    name: str
    status: str = "pending"
    notes: str = ""


@dataclass
class Project:
    name: str
    project_type: str
    created_at: str
    rules: List[Rule]
    steps: List[ProjectStep]
    sources: List[SourceDocument]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "project_type": self.project_type,
            "created_at": self.created_at,
            "rules": [rule.__dict__ for rule in self.rules],
            "steps": [step.__dict__ for step in self.steps],
            "sources": [source.__dict__ for source in self.sources],
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "Project":
        return cls(
            name=payload["name"],
            project_type=payload["project_type"],
            created_at=payload["created_at"],
            rules=[Rule(**rule) for rule in payload.get("rules", [])],
            steps=[ProjectStep(**step) for step in payload.get("steps", [])],
            sources=[SourceDocument(**source) for source in payload.get("sources", [])],
        )


DEFAULT_PIAMV_STEPS = [
    "Project scoping",
    "Baseline definition",
    "Measurement & verification plan",
    "Implementation & commissioning",
    "Data collection",
    "Analysis & savings calculation",
    "Reporting & assurance",
]


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def project_path(name: str) -> Path:
    safe_name = name.strip().replace(" ", "-")
    return DATA_DIR / f"{safe_name}.json"


def load_project(name: str) -> Project:
    path = project_path(name)
    if not path.exists():
        raise SystemExit(f"Project '{name}' not found at {path}.")
    payload = json.loads(path.read_text())
    return Project.from_dict(payload)


def save_project(project: Project) -> None:
    ensure_data_dir()
    path = project_path(project.name)
    path.write_text(json.dumps(project.to_dict(), indent=2))


def init_project(args: argparse.Namespace) -> None:
    if project_path(args.name).exists():
        raise SystemExit(f"Project '{args.name}' already exists.")
    steps = [ProjectStep(name=step) for step in DEFAULT_PIAMV_STEPS]
    project = Project(
        name=args.name,
        project_type="PIAM&V",
        created_at=datetime.utcnow().isoformat(),
        rules=[],
        steps=steps,
        sources=[],
    )
    save_project(project)
    print(f"Initialized project '{args.name}' with {len(steps)} steps.")


def add_rule(args: argparse.Namespace) -> None:
    project = load_project(args.project)
    rule = Rule(
        source=args.source,
        title=args.title,
        text=args.text,
        section=args.section or "",
        page=args.page or "",
    )
    project.rules.append(rule)
    save_project(project)
    print(f"Added rule '{args.title}' from {args.source}.")


def list_rules(args: argparse.Namespace) -> None:
    project = load_project(args.project)
    if not project.rules:
        print("No rules attached yet.")
        return
    for idx, rule in enumerate(project.rules, start=1):
        location = []
        if rule.section:
            location.append(f"section: {rule.section}")
        if rule.page:
            location.append(f"page: {rule.page}")
        location_text = f" ({', '.join(location)})" if location else ""
        print(f"{idx}. [{rule.source}] {rule.title}{location_text}\n   {rule.text}")


def add_source(args: argparse.Namespace) -> None:
    project = load_project(args.project)
    source = SourceDocument(name=args.name, path=args.path, notes=args.notes or "")
    project.sources.append(source)
    save_project(project)
    print(f"Added source '{args.name}' at {args.path}.")


def list_sources(args: argparse.Namespace) -> None:
    project = load_project(args.project)
    if not project.sources:
        print("No sources attached yet.")
        return
    for idx, source in enumerate(project.sources, start=1):
        notes = f" ({source.notes})" if source.notes else ""
        print(f"{idx}. {source.name}: {source.path}{notes}")


def update_step(args: argparse.Namespace) -> None:
    project = load_project(args.project)
    for step in project.steps:
        if step.name.lower() == args.step.lower():
            step.status = args.status
            step.notes = args.notes or step.notes
            save_project(project)
            print(f"Updated step '{step.name}' to status '{step.status}'.")
            return
    available = ", ".join(step.name for step in project.steps)
    raise SystemExit(f"Step '{args.step}' not found. Available steps: {available}")


def show_project(args: argparse.Namespace) -> None:
    project = load_project(args.project)
    print(f"Project: {project.name}")
    print(f"Type: {project.project_type}")
    print(f"Created: {project.created_at}")
    print("\nSteps:")
    for step in project.steps:
        note = f" ({step.notes})" if step.notes else ""
        print(f"- {step.name}: {step.status}{note}")
    print("\nRules:")
    if project.rules:
        for rule in project.rules:
            print(f"- [{rule.source}] {rule.title}")
    else:
        print("- None")

    print("\nSources:")
    if project.sources:
        for source in project.sources:
            notes = f" ({source.notes})" if source.notes else ""
            print(f"- {source.name}: {source.path}{notes}")
    else:
        print("- None")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PIAM&V project console")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize a PIAM&V project")
    init_parser.add_argument("--name", required=True, help="Project name")
    init_parser.set_defaults(func=init_project)

    rule_parser = subparsers.add_parser("add-rule", help="Attach a rule to a project")
    rule_parser.add_argument("--project", required=True, help="Project name")
    rule_parser.add_argument("--source", required=True, help="Rule source (e.g. IPMVP, NSW PIAM&V)")
    rule_parser.add_argument("--title", required=True, help="Rule title")
    rule_parser.add_argument("--text", required=True, help="Rule description")
    rule_parser.add_argument("--section", help="Optional section reference")
    rule_parser.add_argument("--page", help="Optional page reference")
    rule_parser.set_defaults(func=add_rule)

    list_parser = subparsers.add_parser("list-rules", help="List rules for a project")
    list_parser.add_argument("--project", required=True, help="Project name")
    list_parser.set_defaults(func=list_rules)

    source_parser = subparsers.add_parser("add-source", help="Attach a source document to a project")
    source_parser.add_argument("--project", required=True, help="Project name")
    source_parser.add_argument("--name", required=True, help="Source name (e.g. IPMVP 2018)")
    source_parser.add_argument("--path", required=True, help="Path or URL to the source document")
    source_parser.add_argument("--notes", help="Optional notes")
    source_parser.set_defaults(func=add_source)

    list_sources_parser = subparsers.add_parser("list-sources", help="List source documents for a project")
    list_sources_parser.add_argument("--project", required=True, help="Project name")
    list_sources_parser.set_defaults(func=list_sources)

    step_parser = subparsers.add_parser("step", help="Update a project step")
    step_parser.add_argument("--project", required=True, help="Project name")
    step_parser.add_argument("--step", required=True, help="Step name")
    step_parser.add_argument(
        "--status",
        required=True,
        choices=["pending", "in_progress", "complete"],
        help="Status for the step",
    )
    step_parser.add_argument("--notes", help="Optional notes")
    step_parser.set_defaults(func=update_step)

    show_parser = subparsers.add_parser("show", help="Show project summary")
    show_parser.add_argument("--project", required=True, help="Project name")
    show_parser.set_defaults(func=show_project)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

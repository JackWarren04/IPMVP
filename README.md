# PIAM&V Console

A lightweight, local console for setting up and running PIAM&V projects. This is the first project type and is intended to expand to additional project types (e.g., one-day MBM projects, carbon projects on Verra/Gold/Puro, VEU).

## Quick start

```bash
python piamv_console.py init --name demo-project
python piamv_console.py add-source --project demo-project --name "IPMVP 2018" --path "docs/IPMVP-Generally-Accepted-Principles_Final_26OCT2018.pdf" --notes "Generally Accepted Principles"
python piamv_console.py add-rule --project demo-project --source "NSW PIAM&V" --title "Measurement boundary" --text "Define the measurement boundary and time horizon."
python piamv_console.py list-rules --project demo-project
python piamv_console.py list-sources --project demo-project
python piamv_console.py step --project demo-project --step "Baseline definition" --status in_progress
python piamv_console.py show --project demo-project
```

## Project data

Projects are stored under `data/projects/<project-name>.json`. Rules are attached to each project so that the console can evolve as the rules for IPMVP and NSW PIAM&V are provided.

## Next additions (planned)

- Import rules from structured files (JSON/YAML).
- Add templates for other project types (MBM, VEU, carbon standards).
- Integrate reporting outputs and validation checklists.

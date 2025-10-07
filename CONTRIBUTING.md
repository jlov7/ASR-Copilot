# Contributing to ASR Copilot

Thanks for considering a contribution! This guide covers the basics for proposing changes.

## Development Environment
- Clone the repo and install dependencies:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  cd app/frontend && npm install
  ```
- Or launch with Docker Compose:
  ```bash
  docker-compose up --build
  ```
- Or open in GitHub Codespaces (badge in README).

## Branch & Commit Workflow
1. Create a feature branch: `git checkout -b feature/my-improvement`.
2. Run tests and linters:
   ```bash
   pytest
   cd app/frontend && npm run lint && npm run test -- --run
   ```
3. Format via pre-commit hooks (optional but encouraged): `pre-commit run --all-files`.
4. Open a Pull Request describing the motivation, screenshots/GIFs, and testing evidence.

## Adding Adapters
- Implement the adapter under `app/backend/adapters/` by extending the relevant protocol.
- Document configuration in `.env.example` and README Environment section.
- Provide live integration tests with `pytest.mark.live` guards.

## Extending the ROI Model
- Update assumptions or presets via `app/core/roi.py`.
- Add unit tests in `app/tests/test_roi.py`.
- Reflect the change in the ROI panel (React components) and docs (`docs/DATA-SCHEMA.md`).

## Documentation Expectations
- Update README and related docs under `docs/` whenever behavior changes.
- Add demo notes or changelog entries to `docs/CHANGELOG.md`.

## Code of Conduct
All contributors are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md).

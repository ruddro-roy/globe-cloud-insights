# Contributing to GLOBE Cloud Insights

Thank you for your interest in contributing! This project is built for
educators, students, and open-source collaborators, and we welcome
contributions of all kinds.

## Ways to Contribute

- **Bug reports:** Open an [issue](https://github.com/ruddro-roy/globe-cloud-insights/issues) with a clear description
- **Feature requests:** Suggest new analyses, visualisations, or dashboard features
- **Code contributions:** Fix bugs, add features, or improve documentation
- **Educational content:** Add tutorials, lesson plans, or classroom activities
- **Data analysis:** Share interesting findings from the dataset

## Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/<your-username>/globe-cloud-insights.git
cd globe-cloud-insights

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with development dependencies
pip install -e ".[dev,notebooks]"

# Install pre-commit hooks
pre-commit install
```

## Code Standards

- **Style:** PEP 8, enforced by [Black](https://github.com/psf/black) (line length 88)
- **Imports:** Sorted by [isort](https://pycqa.github.io/isort/) with Black-compatible profile
- **Linting:** [flake8](https://flake8.pycqa.org/)
- **Type checking:** [mypy](https://mypy-lang.org/) (non-strict mode)
- **Testing:** [pytest](https://docs.pytest.org/) with ≥90% coverage target

## Pull Request Process

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and add/update tests as needed.

3. **Run quality checks locally:**
   ```bash
   black src/ tests/ app/
   isort src/ tests/ app/
   flake8 src/ tests/ app/ --max-line-length=88 --extend-ignore=E203,W503
   mypy src/ --ignore-missing-imports
   pytest -v
   ```

4. **Commit with a clear message** describing what and why.

5. **Open a pull request** against `main` with a description of your changes.

## Data Ethics

When working with GLOBE observation data:

- **Privacy:** Do not attempt to identify individual observers from coordinate data
- **Attribution:** Always cite the GLOBE Program when using or redistributing data


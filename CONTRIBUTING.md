# Contributing

Thank you for your interest in contributing to this project.

## Getting Started

### Fork the Repository

Fork the repository to your GitHub account.

### Clone the Repository

Clone your fork to a local filesystem path:

```bash
git clone <your-fork-url>
cd <repository-directory>
````

### Create a Virtual Environment

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

Activate the virtual environment according to your operating system:

```bash
# Linux / macOS
source .venv/bin/activate

# Windows — Command Prompt
.venv\Scripts\activate.bat

# Windows — PowerShell
.venv\Scripts\Activate.ps1
```

### Install the Project

Install the project and its development dependencies according to the project's installation instructions.

## Making Changes

Create a dedicated branch for your changes:

```bash
git checkout -b <branch-name>
```

Keep changes focused and avoid including unrelated modifications in the same pull request.

## Testing

Run the project's test suite before submitting your changes.

Ensure that:

* Existing tests pass.
* New functionality has appropriate tests.
* Bug fixes include regression tests where appropriate.
* Code quality checks pass.
* Documentation is updated when necessary.

## Code Quality

Follow the project's established coding conventions and development tools.

Before submitting a pull request, run the project's configured formatting, linting, and type-checking tools.

## Commit Messages

Write clear and concise commit messages that describe the purpose of the change.

Where applicable, follow the project's commit-message conventions.

## Pull Requests

Create a pull request from your branch against the appropriate repository branch.

A pull request should:

* Clearly describe the changes.
* Explain the motivation for the changes.
* Reference related issues where applicable.
* Include relevant tests.
* Include documentation updates where necessary.
* Identify any breaking changes.

Keep pull requests focused and reasonably sized to make review easier.

## Issues

Before opening an issue, search existing issues to determine whether the problem or request has already been reported.

When submitting an issue, use the appropriate issue template and provide all requested information.

For security vulnerabilities, do not open a public issue. Follow the project's security reporting procedure instead.

## Code of Conduct

Contributors are expected to follow the project's Code of Conduct.

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project, unless otherwise stated.

## Questions

For questions, discussions, or general project-related topics, use the project's GitHub Discussions where available.

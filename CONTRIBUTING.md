# Contributing to MSIL to Z80 (GB) Compiler

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

1. Check if the issue already exists in the issue tracker
2. Create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce the problem
   - Expected vs actual behavior
   - Your environment (OS, Python version, etc.)
   - Sample code or DLL that demonstrates the issue

### Suggesting Features

1. Check if the feature has already been requested
2. Create a new issue describing:
   - The problem you're trying to solve
   - Your proposed solution
   - Any alternatives you've considered
   - How it benefits the project

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature/fix
3. Make your changes following the coding standards below
4. Write or update tests as needed
5. Ensure all tests pass
6. Update documentation if needed
7. Submit a pull request with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots for UI changes (if applicable)

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/fsakatauskas/CSharpMSILZ80.git
   cd CSharpMSILZ80
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install .NET SDK for building examples:
   ```bash
   # Download from https://dotnet.microsoft.com/download
   ```

## Coding Standards

### Python Code

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints where appropriate
- Write docstrings for classes and functions
- Keep functions focused and single-purpose
- Use dependency injection pattern where applicable

### C# Code (Examples)

- Follow standard C# naming conventions
- Document SDK methods and hardware registers
- Keep examples simple and educational
- Avoid external dependencies in SDK code

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in present tense (e.g., "Add", "Fix", "Update")
- Keep first line under 72 characters
- Add detailed description if needed

Example:
```
Add support for 32-bit integer arithmetic

Implements software-based 32-bit addition and subtraction
using multiple 16-bit operations on the LR35902 CPU.
```

## Security Guidelines

- **Never commit sensitive data** (API keys, passwords, credentials)
- Review `.gitignore` before committing
- Report security vulnerabilities privately (see SECURITY.md)
- Validate all external inputs
- Document security implications of changes

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

## Questions?

If you have questions, feel free to:
- Open an issue for discussion
- Contact the maintainer through GitHub

Thank you for contributing!

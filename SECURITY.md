# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in this project, please report it responsibly:

1. **Do NOT** open a public issue
2. Contact the maintainer privately through GitHub's security advisory feature
3. Provide detailed information about the vulnerability
4. Allow time for the issue to be addressed before public disclosure

## Security Considerations

### Sensitive Data

This project does NOT and should NOT contain:
- API keys or secrets
- Passwords or credentials
- Private keys or certificates
- Personal information (emails, addresses, etc.)
- Any other sensitive data

### Input Validation

This compiler processes .NET assemblies (DLL files). When using this tool:
- Only compile assemblies from trusted sources
- Be aware that malicious assemblies could potentially exploit vulnerabilities
- The compiler does not execute the .NET code - it only reads the MSIL bytecode

### Generated Code

The compiler generates Game Boy ROM files:
- Generated ROMs execute on Game Boy hardware/emulators with limited attack surface
- No network connectivity or file system access in generated code
- Consider the security implications of any ROM you distribute

### Dependencies

This project uses external dependencies:
- `dnfile` - for reading .NET assemblies
- `injector` - for dependency injection

Regularly check for security updates:
```bash
pip list --outdated
pip install --upgrade dnfile injector
```

## Best Practices

1. **Keep dependencies updated** - Run `pip install --upgrade -r requirements.txt` regularly
2. **Review .gitignore** - Ensure sensitive files are excluded from version control
3. **Validate inputs** - Only compile trusted .NET assemblies
4. **Code review** - Review generated assembly code if security is critical
5. **Environment isolation** - Use virtual environments for Python dependencies

## License Compliance

This project is licensed under Apache License 2.0. When using or distributing:
- Include a copy of the LICENSE file
- Preserve copyright and attribution notices
- Document any modifications made to the source code
- Check licenses of any third-party dependencies

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

Security updates will be applied to the main branch.

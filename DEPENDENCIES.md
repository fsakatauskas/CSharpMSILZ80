# Third-Party Dependencies

This project uses the following third-party libraries:

## Python Dependencies

### dnfile (>= 0.15.0)
- **Purpose**: Parse .NET assemblies (PE files) and read MSIL bytecode
- **License**: MIT License
- **Repository**: https://github.com/malwarefrank/dnfile
- **License Compatibility**: ✅ Compatible with Apache 2.0 (MIT is permissive)

### injector (>= 0.21.0)
- **Purpose**: Dependency injection framework for Python
- **License**: BSD 3-Clause License
- **Repository**: https://github.com/python-injector/injector
- **License Compatibility**: ✅ Compatible with Apache 2.0 (BSD is permissive)

## License Compatibility

All dependencies use permissive licenses (MIT, BSD) that are compatible with this project's Apache 2.0 license. You can:
- Use this software commercially
- Modify and distribute it
- Include it in proprietary software

As long as you:
- Include the original copyright notices
- Include the Apache 2.0 license text
- State significant changes made

## Updating Dependencies

To check for dependency updates:
```bash
pip list --outdated
```

To update dependencies:
```bash
pip install --upgrade -r requirements.txt
```

## Security Considerations

- Regularly check for security updates to dependencies
- Review security advisories for `dnfile` and `injector`
- Use virtual environments to isolate dependencies
- Pin dependency versions in production deployments

## Adding New Dependencies

Before adding new dependencies:
1. Check the license for compatibility with Apache 2.0
2. Verify the dependency is actively maintained
3. Review for known security vulnerabilities
4. Update this file with dependency information
5. Update `requirements.txt`

### Compatible Licenses
- MIT License ✅
- BSD Licenses (2-Clause, 3-Clause) ✅
- Apache 2.0 ✅
- Python Software Foundation License ✅

### Incompatible Licenses
- GPL (copyleft - requires entire project to be GPL) ❌
- AGPL (copyleft with network clause) ❌
- Proprietary/Closed Source ❌

For questions about license compatibility, consult:
- https://www.apache.org/legal/resolved.html
- https://choosealicense.com/appendix/

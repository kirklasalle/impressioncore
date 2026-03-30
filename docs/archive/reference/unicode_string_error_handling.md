# Unicode and String Error Handling in ImpressionCore

**Created:** August 09, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\unicode_string_error_handling.md #reference #unicode #string #error_handling #documentation  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

All error handling, logging, and documentation described here is indexed and searchable via the ImpressionCore Documentation System (IDS). Contributors must ensure all updates and logs are IDS-compliant for full traceability and project-wide searchability.

**Created:** August 9, 2025  
**Author:** GitHub Copilot  
**Tags:** #reference #unicode #string #error_handling #documentation  
**Status:** Active

---

## Encoding Standard

- All file I/O in ImpressionCore uses UTF-8 encoding by default.
- Contributors must not use legacy encodings unless absolutely required and documented.

## Error Handling Policy

- All scripts must log any UnicodeDecodeError, UnicodeEncodeError, or generic string/encoding error with the file path and error type.
- If `errors='ignore'` is used, a warning must be logged that data loss is possible.
- All exceptions during file I/O must be logged with full context for traceability.
- Contributors should prefer explicit error handling and logging over silent failure.

## Example Log Messages

``` text
[UNICODE ERROR] Could not decode file: path/to/file.py | 'utf-8' codec can't decode byte 0x...
[ERROR] Could not read file: path/to/file.py | FileNotFoundError: [Errno 2] No such file or directory
[UNICODE ERROR] Could not encode file: path/to/file.py | 'utf-8' codec can't encode character '\udce2' in position 123: surrogates not allowed
```

## Contributor Quick Reference

- Always use `encoding='utf-8'` for open/read/write.
- Always log the file path and error type on exception.
- If you must use `errors='ignore'`, log a warning.
- Add a docstring to your script describing the encoding/error policy.

---

*This policy ensures robust, transparent, and traceable handling of all string and unicode errors across the ImpressionCore codebase.*

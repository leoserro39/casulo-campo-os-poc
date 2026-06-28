# Controlled Write Policy

The product must never write real/anonymized data into the active import input unless the operator explicitly runs a command with `--write`.

Even after writing, nomination, implementation, production activation and client claims remain blocked.

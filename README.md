# envdiff

> Tool to diff and reconcile .env files across deployment environments

---

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/envdiff.git && cd envdiff && pip install .
```

---

## Usage

Compare two `.env` files and see what's missing, added, or changed:

```bash
envdiff .env.development .env.production
```

**Example output:**

```
+ NEW_FEATURE_FLAG        (only in production)
- DEBUG_TOOLBAR           (only in development)
~ DATABASE_URL            (values differ)
  SECRET_KEY              (match)
```

Reconcile by generating a merged template with all keys:

```bash
envdiff --reconcile .env.development .env.production -o .env.template
```

Check multiple environments at once:

```bash
envdiff .env.development .env.staging .env.production
```

Use `--strict` to exit with a non-zero code if any differences are found — useful in CI pipelines:

```bash
envdiff --strict .env.example .env.production
```

---

## Options

| Flag | Description |
|------|-------------|
| `--reconcile` | Output a merged key template |
| `--strict` | Exit with code 1 if differences exist |
| `--ignore-values` | Compare keys only, ignore values |
| `-o, --output` | Write results to a file |

---

## License

MIT © 2024 yourname
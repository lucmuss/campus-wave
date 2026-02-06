# Release Process

## Versioning

Use semantic version tags: `vMAJOR.MINOR.PATCH`.

## Release Checklist

1. Ensure working tree is clean.
2. Run:
   ```bash
   just ci
   ```
3. Bump version in `pyproject.toml`.
4. Commit and push.
5. Create tag:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

## Publishing

- `publish-to-pypi.yml` publishes on matching tags and manual dispatch.
- `build-binaries.yml` creates binaries and attaches them to GitHub Release assets.

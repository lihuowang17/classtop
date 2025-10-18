# GitHub Actions CI/CD

This directory contains GitHub Actions workflows for automated testing, building, and releasing ClassTop.

## Workflows

### 1. CI (`ci.yml`)

**Trigger:**
- Push to `master`, `main`, or `develop` branches
- Pull requests to `master` or `main`

**Purpose:**
- Runs code quality checks and tests
- Builds the app on multiple platforms to catch issues early
- Ensures code meets quality standards before merging

**Jobs:**
- **Frontend Build**: Builds Vue 3 frontend with Vite
- **Rust Format Check**: Ensures Rust code follows formatting standards
- **Rust Clippy**: Runs Rust linter for code quality
- **Multi-platform Test Build**: Builds on Ubuntu, macOS, and Windows

**Platforms Tested:**
- Ubuntu (latest)
- macOS (latest)
- Windows (latest)

### 2. Release (`release.yml`)

**Trigger:**
- Push tags matching `v*` (e.g., `v1.0.0`)
- Manual workflow dispatch

**Purpose:**
- Builds production-ready binaries for all platforms
- Creates GitHub releases with downloadable installers
- Uses Tauri's official action for cross-platform builds

**Artifacts Generated:**
- **macOS**: Universal binary (.dmg, .app)
- **Windows**: Installer (.msi, .exe)
- **Linux**: AppImage, .deb package

**Release Process:**
1. Creates draft release on GitHub
2. Uploads platform-specific installers
3. Release can be reviewed and published manually

## Usage

### Running CI

CI runs automatically on every push and pull request. To see results:
1. Go to the "Actions" tab in GitHub
2. Click on the latest workflow run
3. View logs for each job

### Creating a Release

1. **Update version** in `package.json` and `src-tauri/Cargo.toml`
2. **Create and push a tag:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. **Monitor the build:**
   - Go to Actions tab
   - Watch the Release workflow
4. **Publish the release:**
   - Go to Releases
   - Edit the draft release
   - Add release notes
   - Click "Publish release"

### Manual Release (Optional)

You can also trigger a release manually:
1. Go to Actions tab
2. Select "Release" workflow
3. Click "Run workflow"
4. Select branch and click "Run"

## Configuration

### Required Secrets

For code signing (optional but recommended):
- `TAURI_SIGNING_PRIVATE_KEY`: Private key for signing Tauri updates
- `TAURI_SIGNING_PRIVATE_KEY_PASSWORD`: Password for the private key

To add secrets:
1. Go to repository Settings > Secrets and variables > Actions
2. Click "New repository secret"
3. Add the secret name and value

### Customization

**Modify CI triggers** in `ci.yml`:
```yaml
on:
  push:
    branches: [your-branch]
```

**Change platforms** in `release.yml`:
```yaml
matrix:
  platform: [ubuntu-22.04, macos-latest, windows-latest]
```

## Troubleshooting

### CI Fails on Specific Platform

Check the workflow logs for the failing platform. Common issues:
- Missing system dependencies (especially on Linux)
- Python version mismatch
- Rust toolchain issues

### Release Build Fails

1. Ensure all dependencies are correctly specified
2. Test local build: `npm run tauri build`
3. Check that icons exist in `src-tauri/icons/`
4. Verify `tauri.bundle.json` configuration

### PyTauri Issues

If builds fail due to Python embedding:
- Ensure Python 3.10+ is specified in workflow
- Check PyTauri version compatibility
- Verify Python dependencies are bundled correctly

## Maintenance

**Update Actions versions** regularly:
```bash
# Check for outdated actions
grep -r "uses:" .github/workflows/
```

**Monitor workflow runs** for deprecation warnings and update accordingly.

## Resources

- [Tauri GitHub Actions](https://tauri.app/v1/guides/building/cross-platform#github-actions)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyTauri Documentation](https://github.com/pytauri/pytauri)

# Building and Publishing the VS Code Extension

Complete guide for building, testing, and publishing the AI Usage Monitor VS Code extension.

---

## Prerequisites

### Required Software

1. **Node.js** (v20 or higher)
   ```bash
   node --version  # Should be 20.x or higher
   ```

2. **npm** (comes with Node.js)
   ```bash
   npm --version
   ```

3. **Visual Studio Code** (v1.85.0 or higher)
   ```bash
   code --version
   ```

4. **TypeScript** (installed via npm)
   ```bash
   npm install -g typescript
   ```

5. **vsce** (VS Code Extension Manager)
   ```bash
   npm install -g @vscode/vsce
   ```

### Optional Tools

- **ovsx** - For publishing to Open VSX Registry
  ```bash
  npm install -g ovsx
  ```

---

## Initial Setup

### 1. Install Dependencies

Navigate to the extension directory and install dependencies:

```bash
cd vscode-extension
npm install
```

This installs:
- TypeScript compiler
- ESLint and TypeScript ESLint
- VS Code types
- Testing framework
- Build tools

### 2. Verify Installation

Check that everything is installed correctly:

```bash
npm run compile  # Should compile without errors
npm run lint     # Should show no errors
```

---

## Development

### 1. Open in VS Code

```bash
code .
```

### 2. Launch Extension Development Host

Press `F5` or:
- Go to Run and Debug (Cmd+Shift+D / Ctrl+Shift+D)
- Select "Run Extension"
- Click the green play button

This opens a new VS Code window with your extension loaded.

### 3. Make Changes

Edit files in `src/`:
- `extension.ts` - Main extension entry point
- `views/` - Tree view providers
- `webviews/` - Dashboard and cost analysis panels
- `utils/` - CLI manager and utilities

### 4. Reload Extension

After making changes:
- In the Extension Development Host window
- Press `Cmd+R` / `Ctrl+R` to reload
- Or use the "Reload Window" command

### 5. Watch Mode

For automatic compilation on save:

```bash
npm run watch
```

Leave this running in a terminal while developing.

---

## Testing

### Manual Testing

1. **Launch Extension Development Host** (F5)
2. **Test each feature:**
   - Overview panel shows data
   - Daily/Monthly views work
   - Dashboard opens and displays charts
   - Cost analysis shows correctly
   - Export functionality works
   - Commands work from palette
   - Refresh updates data
   - Settings are respected

### Unit Testing

```bash
npm run test
```

### Test Checklist

- [ ] Extension activates without errors
- [ ] CLI detection works
- [ ] Tree views populate correctly
- [ ] Dashboard charts render
- [ ] Cost analysis calculates correctly
- [ ] Export to JSON works
- [ ] Export to CSV works
- [ ] Auto-refresh works
- [ ] Settings persist
- [ ] Tool selection works
- [ ] Works in light theme
- [ ] Works in dark theme
- [ ] No console errors

---

## Building

### 1. Clean Build

```bash
npm run compile
```

This compiles TypeScript to JavaScript in the `out/` directory.

### 2. Lint Check

```bash
npm run lint
```

Fix any linting errors before building.

### 3. Package Extension

```bash
npm run package
```

Or manually:

```bash
vsce package
```

This creates `ai-usage-monitor-1.0.0.vsix`.

### 4. Verify Package Contents

```bash
# List files in package
unzip -l ai-usage-monitor-1.0.0.vsix

# Check size (should be <10MB)
ls -lh ai-usage-monitor-1.0.0.vsix
```

---

## Local Installation

### Install VSIX Locally

Test the packaged extension:

```bash
code --install-extension ai-usage-monitor-1.0.0.vsix
```

Or via UI:
1. Open VS Code
2. Extensions → "..." menu → "Install from VSIX..."
3. Select the .vsix file

### Uninstall

```bash
code --uninstall-extension aecs4u.ai-usage-monitor
```

---

## Publishing

### Prepare for Publishing

#### 1. Update Version

In `package.json`:
```json
{
  "version": "1.0.0"  // Increment for each release
}
```

Follow [Semantic Versioning](https://semver.org/):
- `1.0.0` → `1.0.1` - Bug fixes
- `1.0.0` → `1.1.0` - New features
- `1.0.0` → `2.0.0` - Breaking changes

#### 2. Update CHANGELOG

Add entry to `CHANGELOG.md`:
```markdown
## [1.0.1] - 2025-01-25

### Fixed
- Bug fix description

### Added
- New feature description
```

#### 3. Create Icons

Ensure you have:
- `resources/icon.png` (128x128)
- `resources/icon.svg` (activity bar)
- `resources/screenshots/*.png`

See [resources/README.md](resources/README.md) for details.

#### 4. Review README

- [ ] Accurate feature list
- [ ] Working screenshot links
- [ ] Correct version numbers
- [ ] Valid links

### Publish to VS Code Marketplace

#### 1. Create Publisher Account

1. Go to https://marketplace.visualstudio.com/manage
2. Sign in with Microsoft account
3. Create publisher: `aecs4u`

#### 2. Get Personal Access Token (PAT)

1. Go to https://dev.azure.com/
2. User Settings → Personal Access Tokens
3. Create new token:
   - Name: "VS Code Marketplace"
   - Organization: All accessible organizations
   - Scopes: **Marketplace → Manage**
   - Expiration: 90 days (or custom)
4. Copy the token (save it securely!)

#### 3. Login to vsce

```bash
vsce login aecs4u
# Enter your PAT when prompted
```

#### 4. Publish

```bash
vsce publish
```

Or with version bump:

```bash
vsce publish patch  # 1.0.0 → 1.0.1
vsce publish minor  # 1.0.0 → 1.1.0
vsce publish major  # 1.0.0 → 2.0.0
```

#### 5. Verify Publication

1. Go to https://marketplace.visualstudio.com/
2. Search for "AI Usage Monitor"
3. Check that:
   - Version is correct
   - README renders properly
   - Screenshots display
   - Icon shows correctly

### Publish to Open VSX (Optional)

Open VSX is an open-source alternative marketplace:

#### 1. Create Account

1. Go to https://open-vsx.org/
2. Sign in with GitHub
3. Get access token from user settings

#### 2. Publish

```bash
npx ovsx publish -p YOUR_ACCESS_TOKEN
```

---

## Updating

### Publish an Update

1. **Make changes** to the code
2. **Test thoroughly** in Extension Development Host
3. **Update version** in package.json
4. **Update CHANGELOG** with changes
5. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push
   ```
6. **Create git tag**:
   ```bash
   git tag v1.0.1
   git push --tags
   ```
7. **Publish**:
   ```bash
   vsce publish
   ```

### Unpublish (Emergency Only)

**Warning**: This removes the extension completely.

```bash
vsce unpublish aecs4u.ai-usage-monitor
```

Better approach: Publish a fixed version immediately.

---

## CI/CD Automation

### GitHub Actions

Create `.github/workflows/publish-extension.yml`:

```yaml
name: Publish Extension

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        working-directory: vscode-extension
        run: npm ci

      - name: Lint
        working-directory: vscode-extension
        run: npm run lint

      - name: Compile
        working-directory: vscode-extension
        run: npm run compile

      - name: Package
        working-directory: vscode-extension
        run: npm run package

      - name: Publish to Marketplace
        working-directory: vscode-extension
        run: npx vsce publish -p ${{ secrets.VSCE_PAT }}

      - name: Publish to Open VSX
        working-directory: vscode-extension
        run: npx ovsx publish -p ${{ secrets.OVSX_PAT }}
        continue-on-error: true
```

Add secrets to GitHub:
- `VSCE_PAT` - Visual Studio Marketplace token
- `OVSX_PAT` - Open VSX token

---

## Troubleshooting

### Build Errors

**Error**: `Cannot find module '@types/vscode'`

**Solution**:
```bash
npm install --save-dev @types/vscode
```

**Error**: TypeScript compilation errors

**Solution**:
```bash
npm run compile  # See specific errors
# Fix TypeScript errors in src/
```

### Publishing Errors

**Error**: `ERROR Failed request: (401)`

**Solution**: PAT expired or invalid
```bash
vsce login aecs4u  # Re-login with new PAT
```

**Error**: `ERROR Missing publisher name`

**Solution**: Add to package.json:
```json
{
  "publisher": "aecs4u"
}
```

**Error**: `ERROR Missing repository`

**Solution**: Add to package.json:
```json
{
  "repository": {
    "type": "git",
    "url": "https://github.com/aecs4u/ai-usage-monitor.git"
  }
}
```

### Runtime Errors

**Error**: "Cannot find module 'vscode'"

**Solution**: Don't bundle vscode module (it's provided by VS Code)

**Error**: Charts not loading

**Solution**: Check CSP and script sources in webview HTML

---

## Best Practices

### Version Management
- Use semantic versioning
- Tag releases in git
- Maintain CHANGELOG.md
- Test before publishing

### Code Quality
- Run linter before commit
- Write clear commit messages
- Keep dependencies updated
- Document complex code

### Testing
- Test in both light and dark themes
- Test on Windows, macOS, Linux
- Test with different VS Code versions
- Test with real usage data

### Security
- Never commit PAT tokens
- Use GitHub secrets for CI/CD
- Validate user input
- Handle errors gracefully

---

## Release Checklist

Before each release:

- [ ] Version bumped in package.json
- [ ] CHANGELOG.md updated
- [ ] All tests passing
- [ ] Linting clean
- [ ] README accurate
- [ ] Screenshots current
- [ ] Icons present
- [ ] Tested in Extension Development Host
- [ ] Tested from VSIX
- [ ] Git committed and pushed
- [ ] Git tagged
- [ ] Published to marketplace
- [ ] Verified in marketplace
- [ ] Published to Open VSX (optional)
- [ ] GitHub release created

---

## Resources

- **VS Code Extension API**: https://code.visualstudio.com/api
- **Publishing Guide**: https://code.visualstudio.com/api/working-with-extensions/publishing-extension
- **vsce Documentation**: https://github.com/microsoft/vscode-vsce
- **Extension Manifest**: https://code.visualstudio.com/api/references/extension-manifest
- **Extension Guidelines**: https://code.visualstudio.com/api/references/extension-guidelines

---

**Ready to build!** 🚀

Follow this guide step-by-step for a successful extension release.

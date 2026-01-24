# GitHub Automation Guide

Complete reference for all GitHub Actions workflows and automated processes in AI Usage Monitor.

---

## Overview

This project uses GitHub Actions for continuous integration, automated releases, community management, and quality assurance. All workflows are in `.github/workflows/`.

---

## Workflows

### 1. Testing & Quality (`test.yml`)

**Trigger:** Every push and pull request
**Purpose:** Ensure code quality and test coverage

**What it does:**
- Runs pytest across multiple Python versions (3.9-3.12)
- Executes linters (ruff, mypy)
- Validates code formatting
- Reports test failures

**Manual trigger:**
```bash
gh workflow run test.yml
```

---

### 2. Linting (`lint.yml`)

**Trigger:** Every push and pull request
**Purpose:** Enforce code style and quality standards

**What it does:**
- Runs ruff for linting
- Checks code formatting with black
- Validates type hints with mypy
- Reports style violations

**Fix lint issues locally:**
```bash
ruff check --fix src/
black src/
mypy src/
```

---

### 3. Release Automation (`release.yml`)

**Trigger:** When a new tag is pushed (e.g., `v4.1.0`)
**Purpose:** Automate the release process

**What it does:**
- Creates GitHub release with notes
- Builds Python package (wheel + sdist)
- Publishes to PyPI
- Updates changelog
- Notifies maintainers

**Create a release:**
```bash
# 1. Update version
bumpversion patch  # or minor, major

# 2. Push tag
git push --tags

# 3. Workflow runs automatically
```

---

### 4. Version Bump (`version-bump.yml`)

**Trigger:** Manual or on specific labels
**Purpose:** Automate semantic versioning

**What it does:**
- Bumps version based on commit type
- Updates `pyproject.toml`
- Creates commit and tag
- Triggers release workflow

**Trigger manually:**
```bash
gh workflow run version-bump.yml -f version=patch  # or minor, major
```

---

### 5. Auto Label PRs (`auto-label.yml`) ✨ NEW

**Trigger:** When PR is opened or updated
**Purpose:** Automatically label PRs based on changed files

**What it does:**
- Detects changed files in PR
- Applies relevant labels (documentation, core, adapters, etc.)
- Keeps labels in sync with changes

**Label mappings:** See `.github/labeler.yml`

**Labels applied:**
- `documentation` - Docs, README, markdown files
- `adapters` - Adapter implementations
- `core` - Core functionality
- `ui` - UI components
- `cli` - CLI changes
- `monitoring` - Monitoring code
- `tests` - Test files
- `telemetry` - Telemetry code
- `dependencies` - Package dependencies
- `ci-cd` - GitHub Actions, CI/CD
- `scripts` - Utility scripts

---

### 6. Welcome Contributors (`welcome.yml`) ✨ NEW

**Trigger:** First issue or PR from a contributor
**Purpose:** Welcome new community members

**What it does:**
- Detects first-time contributors
- Posts welcoming message
- Links to contributing guide
- Provides helpful resources

**Messages:**
- **First issue:** Links to docs, discussions, contributing guide
- **First PR:** Checklist of review requirements

---

### 7. Stale Management (`stale.yml`) ✨ NEW

**Trigger:** Daily at midnight UTC
**Purpose:** Keep repository clean and organized

**What it does:**
- Marks inactive issues as stale after 60 days
- Marks inactive PRs as stale after 30 days
- Closes stale issues after 14 more days
- Closes stale PRs after 7 more days
- Exempts pinned, security, and good first issues

**Prevent closure:**
- Comment on the issue/PR
- Add new information
- Push new commits (for PRs)

**Exempt labels:**
- `pinned` - Never becomes stale
- `security` - Never becomes stale
- `good first issue` - Never becomes stale
- `help wanted` - Never becomes stale

---

### 8. Demo Update Reminder (`demo-reminder.yml`) ✨ NEW

**Trigger:** When a release is published
**Purpose:** Remind maintainers to update demo recordings

**What it does:**
- Detects new releases
- Creates reminder issue
- Links to demo recording guide
- Suggests when update is needed

**What to do:**
1. Check if UI/UX changed significantly
2. Re-record demo if needed: `./scripts/record-demo.sh`
3. Upload new demo to asciinema.org
4. Update README.md link
5. Close the reminder issue

---

### 9. Code Coverage (`coverage.yml`) ✨ NEW

**Trigger:** Push to main, pull requests
**Purpose:** Track and report test coverage

**What it does:**
- Runs tests with coverage measurement
- Generates HTML coverage report
- Posts coverage comment on PRs
- Uploads to Codecov (if token configured)
- Enforces 70% minimum coverage

**View coverage locally:**
```bash
pytest src/tests/ --cov=ai_usage_monitor --cov-report=html
open htmlcov/index.html
```

**Coverage artifacts:**
- Available in workflow run for 30 days
- Download via GitHub Actions UI

---

## Dependabot

**File:** `.github/dependabot.yml`
**Purpose:** Automated dependency updates

**What it monitors:**
- Python dependencies (`pip`)
- GitHub Actions versions
- Docker base images

**Schedule:** Weekly on Mondays at 9am UTC

**What it does:**
- Creates PRs for dependency updates
- Labels PRs with `dependencies`
- Limits to 5 Python PRs, 3 Actions PRs
- Ignores major version bumps for stable deps

**Managing Dependabot PRs:**
```bash
# List open Dependabot PRs
gh pr list --label dependencies

# Merge a Dependabot PR
gh pr merge <PR-number> --squash

# Close without merging
gh pr close <PR-number>
```

---

## Secrets Configuration

Some workflows require secrets to be configured in repository settings.

### Required Secrets

1. **PYPI_API_TOKEN** (for `release.yml`)
   - Used to publish packages to PyPI
   - Get from: https://pypi.org/manage/account/token/
   - Scope: Project-specific token for ai-usage-monitor

2. **CODECOV_TOKEN** (optional, for `coverage.yml`)
   - Used to upload coverage to Codecov
   - Get from: https://codecov.io/
   - Free for open source projects

### Configure Secrets

```bash
# Via GitHub CLI
gh secret set PYPI_API_TOKEN < token.txt

# Or manually
# Settings → Secrets and variables → Actions → New repository secret
```

---

## Manual Workflow Triggers

Most workflows can be triggered manually via GitHub CLI or UI.

### Via GitHub CLI

```bash
# List available workflows
gh workflow list

# Run a workflow
gh workflow run test.yml

# Run with inputs
gh workflow run version-bump.yml -f version=minor

# View workflow runs
gh run list --workflow=test.yml

# Watch a running workflow
gh run watch
```

### Via GitHub UI

1. Go to **Actions** tab
2. Select workflow from left sidebar
3. Click **Run workflow** button
4. Fill in inputs (if required)
5. Click **Run workflow**

---

## Workflow Status Badges

Add workflow status badges to README:

```markdown
![Tests](https://github.com/aecs4u/ai-usage-monitor/workflows/Tests/badge.svg)
![Lint](https://github.com/aecs4u/ai-usage-monitor/workflows/Lint/badge.svg)
![Coverage](https://codecov.io/gh/aecs4u/ai-usage-monitor/branch/main/graph/badge.svg)
```

---

## Best Practices

### For Maintainers

1. **Review Dependabot PRs weekly**
   - Check for breaking changes
   - Run tests locally for major updates
   - Merge small patches quickly

2. **Monitor stale issues**
   - Check stale label weekly
   - Close truly inactive issues
   - Remove stale label if still relevant

3. **Update demo after UI changes**
   - Follow demo-reminder issues
   - Re-record when significant changes land
   - Keep demo under 60 seconds

4. **Respond to first-time contributors**
   - Thank them for their contribution
   - Provide constructive feedback
   - Help them succeed

### For Contributors

1. **Check workflow status before merging**
   - All tests must pass
   - Linting must pass
   - Coverage should not decrease

2. **Let automation handle labels**
   - Don't manually add labels
   - Auto-labeler will apply correct labels
   - Maintainers can adjust if needed

3. **Keep PRs focused**
   - One feature per PR
   - Triggers appropriate auto-labels
   - Easier to review and merge

---

## Troubleshooting

### Workflow Failures

**Tests failing:**
```bash
# Run tests locally
pytest src/tests/ -v

# Check specific test
pytest src/tests/test_file.py::test_name -v
```

**Linting failures:**
```bash
# Fix automatically
ruff check --fix src/
black src/

# Check types
mypy src/
```

**Release failing:**
- Check PYPI_API_TOKEN is set
- Verify token has correct scope
- Ensure version is unique (not already published)

**Coverage failing:**
- Coverage dropped below 70%
- Add tests for new code
- Check coverage locally: `pytest --cov`

### Dependabot Issues

**Too many PRs:**
- Adjust `open-pull-requests-limit` in `.github/dependabot.yml`
- Close unnecessary PRs
- Merge related PRs together

**Breaking updates:**
- Review release notes
- Test locally before merging
- Add to ignore list if needed

### Stale Bot Issues

**Issue marked stale incorrectly:**
- Comment to remove stale label
- Add `pinned` label to prevent future staling
- Adjust `days-before-stale` in workflow

---

## Monitoring Workflows

### View All Workflows

```bash
# List all workflows
gh workflow list

# View specific workflow details
gh workflow view test.yml
```

### View Workflow Runs

```bash
# Recent runs across all workflows
gh run list

# Runs for specific workflow
gh run list --workflow=test.yml

# Failed runs only
gh run list --status=failure
```

### View Workflow Logs

```bash
# View logs for latest run
gh run view --log

# View logs for specific run
gh run view 1234567890 --log

# Download logs
gh run download 1234567890
```

---

## Customization

### Add New Workflow

1. Create `.github/workflows/my-workflow.yml`
2. Define trigger, jobs, steps
3. Test with manual trigger
4. Document in this guide

**Template:**
```yaml
name: My Workflow

on:
  push:
    branches: [main]

jobs:
  my-job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Do something
        run: echo "Hello"
```

### Modify Existing Workflow

1. Edit workflow file
2. Commit and push
3. Watch workflow run
4. Iterate until working
5. Update docs

---

## Resources

- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **Workflow Syntax:** https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions
- **GitHub CLI:** https://cli.github.com/
- **Dependabot:** https://docs.github.com/en/code-security/dependabot
- **Codecov:** https://docs.codecov.com/

---

## Summary of Automation

| Workflow | Trigger | Purpose | Status |
|----------|---------|---------|--------|
| Tests | Push, PR | Run test suite | ✅ Active |
| Lint | Push, PR | Code quality | ✅ Active |
| Release | Tag push | Publish to PyPI | ✅ Active |
| Version Bump | Manual | Update version | ✅ Active |
| Auto Label | PR opened | Label PRs | ✨ New |
| Welcome | First contribution | Welcome message | ✨ New |
| Stale | Daily | Clean up inactive | ✨ New |
| Demo Reminder | Release | Update demo | ✨ New |
| Coverage | Push, PR | Track coverage | ✨ New |
| Dependabot | Weekly | Update deps | ✨ New |

**Legend:**
- ✅ Active - Already existed
- ✨ New - Just added

---

## Questions?

- Open an issue: https://github.com/aecs4u/ai-usage-monitor/issues
- Discussions: https://github.com/aecs4u/ai-usage-monitor/discussions
- Email maintainers: See CONTRIBUTORS.md

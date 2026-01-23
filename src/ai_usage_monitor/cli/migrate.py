"""Migration utilities for upgrading from claude-monitor to ai-usage-monitor.

This module handles migration of:
- Configuration directory (~/.claude-monitor -> ~/.ai-usage-monitor)
- Last used parameters
- User preferences
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

OLD_CONFIG_DIR = Path.home() / ".claude-monitor"
NEW_CONFIG_DIR = Path.home() / ".ai-usage-monitor"


def check_migration_needed() -> bool:
    """Check if migration from old config directory is needed.

    Returns:
        True if old config exists and new config doesn't.
    """
    old_exists = OLD_CONFIG_DIR.exists()
    new_exists = NEW_CONFIG_DIR.exists()

    if old_exists and not new_exists:
        return True
    if old_exists and new_exists:
        # Both exist - check if old has newer data
        old_params = OLD_CONFIG_DIR / "last_used.json"
        new_params = NEW_CONFIG_DIR / "last_used.json"

        if old_params.exists() and not new_params.exists():
            return True

    return False


def migrate_config(
    force: bool = False,
    dry_run: bool = False,
) -> bool:
    """Migrate configuration from old directory to new.

    Args:
        force: Force migration even if new config exists
        dry_run: Only show what would be done

    Returns:
        True if migration was successful or not needed.
    """
    if not OLD_CONFIG_DIR.exists():
        logger.info("No old configuration found at %s", OLD_CONFIG_DIR)
        return True

    if NEW_CONFIG_DIR.exists() and not force:
        logger.info("New configuration already exists at %s", NEW_CONFIG_DIR)
        return True

    if dry_run:
        logger.info("[DRY RUN] Would migrate %s -> %s", OLD_CONFIG_DIR, NEW_CONFIG_DIR)
        _log_migration_plan()
        return True

    try:
        # Create new directory
        NEW_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Migrate last_used.json
        old_params = OLD_CONFIG_DIR / "last_used.json"
        if old_params.exists():
            _migrate_last_used_params(old_params)

        # Copy any other config files
        for item in OLD_CONFIG_DIR.iterdir():
            if item.is_file() and item.name != "last_used.json":
                dest = NEW_CONFIG_DIR / item.name
                if not dest.exists():
                    shutil.copy2(item, dest)
                    logger.info("Copied %s", item.name)

        logger.info("Migration completed successfully")
        return True

    except Exception as e:
        logger.error("Migration failed: %s", e)
        return False


def _migrate_last_used_params(old_params_path: Path) -> None:
    """Migrate last_used.json with any necessary transformations."""
    try:
        with open(old_params_path) as f:
            params = json.load(f)

        # Add tool parameter if not present (default to claude-code)
        if "tool" not in params:
            params["tool"] = "claude-code"

        # Write to new location
        new_params_path = NEW_CONFIG_DIR / "last_used.json"
        with open(new_params_path, "w") as f:
            json.dump(params, f, indent=2)

        logger.info("Migrated last_used.json with tool=%s", params.get("tool"))

    except Exception as e:
        logger.warning("Failed to migrate last_used.json: %s", e)


def _log_migration_plan() -> None:
    """Log what files would be migrated."""
    if not OLD_CONFIG_DIR.exists():
        return

    logger.info("Files to migrate from %s:", OLD_CONFIG_DIR)
    for item in OLD_CONFIG_DIR.iterdir():
        if item.is_file():
            logger.info("  - %s", item.name)


def auto_migrate_if_needed() -> None:
    """Automatically migrate if old config exists and new doesn't.

    This is called during application startup to seamlessly
    migrate users from claude-monitor to ai-usage-monitor.
    """
    if check_migration_needed():
        logger.info("Detected old configuration, migrating...")
        migrate_config()


def get_config_dir() -> Path:
    """Get the current configuration directory.

    Handles migration automatically if needed.

    Returns:
        Path to configuration directory.
    """
    auto_migrate_if_needed()
    return NEW_CONFIG_DIR


def cleanup_old_config(confirm: bool = False) -> bool:
    """Remove old configuration directory after migration.

    Args:
        confirm: Must be True to actually delete

    Returns:
        True if cleanup was successful.
    """
    if not OLD_CONFIG_DIR.exists():
        logger.info("No old configuration to clean up")
        return True

    if not confirm:
        logger.warning(
            "Would remove %s. Pass confirm=True to actually delete.",
            OLD_CONFIG_DIR,
        )
        return False

    try:
        shutil.rmtree(OLD_CONFIG_DIR)
        logger.info("Removed old configuration directory: %s", OLD_CONFIG_DIR)
        return True
    except Exception as e:
        logger.error("Failed to remove old config: %s", e)
        return False


def main() -> None:
    """CLI entry point for migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate configuration from claude-monitor to ai-usage-monitor"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force migration even if new config exists",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove old config directory after migration",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if check_migration_needed() or args.force:
        success = migrate_config(force=args.force, dry_run=args.dry_run)
        if success and args.cleanup and not args.dry_run:
            cleanup_old_config(confirm=True)
    else:
        print("No migration needed.")


if __name__ == "__main__":
    main()

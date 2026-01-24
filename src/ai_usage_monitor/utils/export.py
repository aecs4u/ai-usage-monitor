"""Export utilities for usage data.

This module provides functions to export aggregated usage data to various formats
(JSON, CSV) for further analysis or reporting.
"""

import csv
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

logger = logging.getLogger(__name__)


def export_to_json(
    data: List[Dict[str, Any]],
    output_path: Optional[Path] = None,
    view_type: str = "daily",
    tool_name: Optional[str] = None,
) -> bool:
    """Export usage data to JSON format.

    Args:
        data: Aggregated usage data
        output_path: Output file path (None for stdout)
        view_type: Type of view ('daily' or 'monthly')
        tool_name: Optional tool name for metadata

    Returns:
        True if export succeeded, False otherwise
    """
    try:
        export_data = {
            "format": "ai-usage-monitor-export",
            "version": "1.0",
            "view_type": view_type,
            "tool": tool_name or "unknown",
            "exported_at": _get_current_timestamp(),
            "data": data,
        }

        if output_path:
            # Write to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, default=str)
            logger.info(f"Exported {len(data)} entries to {output_path}")
            print(f"✓ Exported to: {output_path}")
        else:
            # Write to stdout
            json.dump(export_data, sys.stdout, indent=2, default=str)
            sys.stdout.write("\n")

        return True

    except Exception as e:
        logger.error(f"Failed to export to JSON: {e}", exc_info=True)
        print(f"✗ Export failed: {e}", file=sys.stderr)
        return False


def export_to_csv(
    data: List[Dict[str, Any]],
    output_path: Optional[Path] = None,
    view_type: str = "daily",
) -> bool:
    """Export usage data to CSV format.

    Args:
        data: Aggregated usage data
        output_path: Output file path (None for stdout)
        view_type: Type of view ('daily' or 'monthly')

    Returns:
        True if export succeeded, False otherwise
    """
    try:
        if not data:
            logger.warning("No data to export")
            return False

        # Define columns based on view type
        if view_type == "daily":
            fieldnames = [
                "date",
                "tools",
                "models",
                "input_tokens",
                "output_tokens",
                "cache_creation_tokens",
                "cache_read_tokens",
                "total_tokens",
                "total_cost",
                "entries_count",
            ]
        else:  # monthly
            fieldnames = [
                "month",
                "tools",
                "models",
                "input_tokens",
                "output_tokens",
                "cache_creation_tokens",
                "cache_read_tokens",
                "total_tokens",
                "total_cost",
                "entries_count",
            ]

        if output_path:
            # Write to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(data)
            logger.info(f"Exported {len(data)} entries to {output_path}")
            print(f"✓ Exported to: {output_path}")
        else:
            # Write to stdout
            writer = csv.DictWriter(
                sys.stdout, fieldnames=fieldnames, extrasaction="ignore"
            )
            writer.writeheader()
            writer.writerows(data)

        return True

    except Exception as e:
        logger.error(f"Failed to export to CSV: {e}", exc_info=True)
        print(f"✗ Export failed: {e}", file=sys.stderr)
        return False


def _get_current_timestamp() -> str:
    """Get current timestamp in ISO format.

    Returns:
        ISO formatted timestamp string
    """
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def validate_export_format(format_str: str) -> bool:
    """Validate export format string.

    Args:
        format_str: Export format ('json' or 'csv')

    Returns:
        True if valid, False otherwise
    """
    return format_str.lower() in ["json", "csv"]


def get_default_export_filename(
    view_type: str, export_format: str, tool_name: Optional[str] = None
) -> str:
    """Generate default export filename.

    Args:
        view_type: Type of view ('daily' or 'monthly')
        export_format: Export format ('json' or 'csv')
        tool_name: Optional tool name

    Returns:
        Default filename string
    """
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tool_part = f"_{tool_name}" if tool_name and tool_name != "all" else ""
    return f"ai_usage_{view_type}{tool_part}_{timestamp}.{export_format}"

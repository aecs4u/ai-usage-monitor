"""Table views for daily and monthly statistics display.

This module provides UI components for displaying aggregated usage data
in table format using Rich library.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Removed theme import - using direct styles
from ai_usage_monitor.utils.formatting import format_currency, format_number

logger = logging.getLogger(__name__)


class TableViewsController:
    """Controller for table-based views (daily, monthly)."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize the table views controller.

        Args:
            console: Optional Console instance for rich output
        """
        self.console = console
        # Define simple styles
        self.key_style = "cyan"
        self.value_style = "white"
        self.accent_style = "yellow"
        self.success_style = "green"
        self.warning_style = "yellow"
        self.header_style = "bold cyan"
        self.table_header_style = "bold"
        self.border_style = "bright_blue"

    def _create_base_table(
        self, title: str, period_column_name: str, period_column_width: int
    ) -> Table:
        """Create a base table with common structure.

        Args:
            title: Table title
            period_column_name: Name for the period column ('Date' or 'Month')
            period_column_width: Width for the period column

        Returns:
            Rich Table object with columns added
        """
        table = Table(
            title=title,
            title_style="bold cyan",
            show_header=True,
            header_style="bold",
            border_style="bright_blue",
            expand=True,
            show_lines=True,
        )

        # Add columns
        table.add_column(
            period_column_name, style=self.key_style, width=period_column_width
        )
        table.add_column("Models", style=self.value_style, width=20)
        table.add_column("Input", style=self.value_style, justify="right", width=12)
        table.add_column("Output", style=self.value_style, justify="right", width=12)
        table.add_column(
            "Cache Create", style=self.value_style, justify="right", width=12
        )
        table.add_column(
            "Cache Read", style=self.value_style, justify="right", width=12
        )
        table.add_column(
            "Total Tokens", style=self.accent_style, justify="right", width=12
        )
        table.add_column(
            "Cost*", style=self.success_style, justify="right", width=10
        )

        return table

    def _add_data_rows(
        self, table: Table, data_list: List[Dict[str, Any]], period_key: str
    ) -> None:
        """Add data rows to the table.

        Args:
            table: Table to add rows to
            data_list: List of data dictionaries
            period_key: Key to use for period column ('date' or 'month')
        """
        for data in data_list:
            models_text = self._format_models(data["models_used"])
            total_tokens = (
                data["input_tokens"]
                + data["output_tokens"]
                + data["cache_creation_tokens"]
                + data["cache_read_tokens"]
            )

            table.add_row(
                data[period_key],
                models_text,
                format_number(data["input_tokens"]),
                format_number(data["output_tokens"]),
                format_number(data["cache_creation_tokens"]),
                format_number(data["cache_read_tokens"]),
                format_number(total_tokens),
                format_currency(data["total_cost"]),
            )

    def _add_totals_row(self, table: Table, totals: Dict[str, Any]) -> None:
        """Add totals row to the table.

        Args:
            table: Table to add totals to
            totals: Dictionary with total statistics
        """
        # Add separator
        table.add_row("", "", "", "", "", "", "", "")

        # Add totals row
        table.add_row(
            Text("Total", style=self.accent_style),
            "",
            Text(format_number(totals["input_tokens"]), style=self.accent_style),
            Text(format_number(totals["output_tokens"]), style=self.accent_style),
            Text(
                format_number(totals["cache_creation_tokens"]), style=self.accent_style
            ),
            Text(format_number(totals["cache_read_tokens"]), style=self.accent_style),
            Text(format_number(totals["total_tokens"]), style=self.accent_style),
            Text(format_currency(totals["total_cost"]), style=self.success_style),
        )

    def create_daily_table(
        self,
        daily_data: List[Dict[str, Any]],
        totals: Dict[str, Any],
        timezone: str = "UTC",
    ) -> Table:
        """Create a daily statistics table.

        Args:
            daily_data: List of daily aggregated data
            totals: Total statistics
            timezone: Timezone for display

        Returns:
            Rich Table object
        """
        # Create base table
        table = self._create_base_table(
            title=f"Claude Code Token Usage Report - Daily ({timezone})",
            period_column_name="Date",
            period_column_width=12,
        )

        # Add data rows
        self._add_data_rows(table, daily_data, "date")

        # Add totals
        self._add_totals_row(table, totals)

        return table

    def create_monthly_table(
        self,
        monthly_data: List[Dict[str, Any]],
        totals: Dict[str, Any],
        timezone: str = "UTC",
    ) -> Table:
        """Create a monthly statistics table.

        Args:
            monthly_data: List of monthly aggregated data
            totals: Total statistics
            timezone: Timezone for display

        Returns:
            Rich Table object
        """
        # Create base table
        table = self._create_base_table(
            title=f"Claude Code Token Usage Report - Monthly ({timezone})",
            period_column_name="Month",
            period_column_width=10,
        )

        # Add data rows
        self._add_data_rows(table, monthly_data, "month")

        # Add totals
        self._add_totals_row(table, totals)

        return table

    def create_summary_panel(
        self,
        view_type: str,
        totals: Dict[str, Any],
        period: str,
        plan: str = "custom",
        num_months: int = 1,
        data_range: Optional[str] = None,
    ) -> Panel:
        """Create a summary panel for the table view with savings calculations.

        Args:
            view_type: Type of view ('daily' or 'monthly')
            totals: Total statistics
            period: Period description
            plan: Plan type for savings calculation
            num_months: Number of months in the period (for subscription cost calculation)
            data_range: Optional string showing full data range available

        Returns:
            Rich Panel object
        """
        from ai_usage_monitor.core.plans import Plans

        api_cost = totals["total_cost"]
        monthly_price = Plans.get_monthly_price(plan)
        is_subscription = Plans.is_subscription_plan(plan)

        # Create summary text
        summary_lines = [
            f"📊 {view_type.capitalize()} Usage Summary - {period}",
            "",
            f"Total Tokens: {format_number(totals['total_tokens'])}",
            f"API Equivalent Cost: {format_currency(api_cost)}",
            f"Entries: {format_number(totals['entries_count'])}",
        ]

        # Add data range info if provided
        if data_range:
            summary_lines.append(f"📅 Data Range: {data_range}")

        # Add savings calculation for subscription plans
        if is_subscription and monthly_price > 0:
            subscription_cost = monthly_price * num_months
            savings = api_cost - subscription_cost
            if api_cost > 0:
                savings_pct = (savings / api_cost) * 100
            else:
                savings_pct = 0.0

            summary_lines.extend([
                "",
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                f"💰 SUBSCRIPTION SAVINGS ({plan.upper()} Plan)",
                f"   Subscription Cost: {format_currency(subscription_cost)} ({num_months} mo × ${monthly_price:.0f})",
                f"   You Saved: {format_currency(savings)} ({savings_pct:.1f}%)",
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            ])
        else:
            summary_lines.extend([
                "",
                "*Cost = API-equivalent pricing",
            ])

        summary_text = Text("\n".join(summary_lines), style=self.value_style)

        # Create panel
        panel = Panel(
            Align.center(summary_text),
            title="Summary",
            title_align="center",
            border_style=self.border_style,
            expand=False,
            padding=(1, 2),
        )

        return panel

    def _format_models(self, models: List[str]) -> str:
        """Format model names for display.

        Args:
            models: List of model names

        Returns:
            Formatted string of model names
        """
        if not models:
            return "No models"

        # Create bullet list
        if len(models) == 1:
            return models[0]
        elif len(models) <= 3:
            return "\n".join([f"• {model}" for model in models])
        else:
            # Truncate long lists
            first_two = models[:2]
            remaining_count = len(models) - 2
            formatted = "\n".join([f"• {model}" for model in first_two])
            formatted += f"\n• ...and {remaining_count} more"
            return formatted

    def create_month_over_month_panel(
        self, monthly_data: List[Dict[str, Any]], plan: str
    ) -> Panel:
        """Create a month-over-month comparison panel.

        Args:
            monthly_data: List of monthly aggregated data
            plan: Plan type for subscription info

        Returns:
            Rich Panel with month-over-month statistics
        """
        from ai_usage_monitor.core.plans import Plans

        monthly_price = Plans.get_monthly_price(plan)
        is_subscription = Plans.is_subscription_plan(plan)

        lines = ["📈 MONTH-OVER-MONTH COMPARISON", ""]

        # Create comparison table
        table = Table(
            show_header=True,
            header_style="bold",
            border_style="dim",
            expand=False,
            show_lines=False,
        )
        table.add_column("Month", style=self.key_style, width=10)
        table.add_column("Tokens", style=self.value_style, justify="right", width=14)
        table.add_column("Δ Tokens", style=self.value_style, justify="right", width=12)
        table.add_column("API Cost", style=self.value_style, justify="right", width=10)
        table.add_column("Δ Cost", style=self.value_style, justify="right", width=10)
        if is_subscription:
            table.add_column("Savings", style=self.success_style, justify="right", width=12)

        prev_tokens = None
        prev_cost = None

        for data in monthly_data:
            month = data["month"]
            total_tokens = (
                data["input_tokens"]
                + data["output_tokens"]
                + data["cache_creation_tokens"]
                + data["cache_read_tokens"]
            )
            api_cost = data["total_cost"]

            # Calculate deltas
            if prev_tokens is not None:
                token_delta = total_tokens - prev_tokens
                token_delta_str = f"{'+' if token_delta >= 0 else ''}{format_number(token_delta)}"
                token_delta_style = "green" if token_delta < 0 else ("red" if token_delta > 0 else "white")
            else:
                token_delta_str = "—"
                token_delta_style = "dim"

            if prev_cost is not None:
                cost_delta = api_cost - prev_cost
                cost_delta_str = f"{'+' if cost_delta >= 0 else '-'}${abs(cost_delta):.2f}"
                cost_delta_style = "green" if cost_delta < 0 else ("red" if cost_delta > 0 else "white")
            else:
                cost_delta_str = "—"
                cost_delta_style = "dim"

            # Calculate savings for subscription plans
            if is_subscription and monthly_price > 0:
                savings = api_cost - monthly_price
                savings_pct = (savings / api_cost * 100) if api_cost > 0 else 0
                savings_str = f"${savings:.2f} ({savings_pct:.0f}%)"
                table.add_row(
                    month,
                    format_number(total_tokens),
                    Text(token_delta_str, style=token_delta_style),
                    format_currency(api_cost),
                    Text(cost_delta_str, style=cost_delta_style),
                    savings_str,
                )
            else:
                table.add_row(
                    month,
                    format_number(total_tokens),
                    Text(token_delta_str, style=token_delta_style),
                    format_currency(api_cost),
                    Text(cost_delta_str, style=cost_delta_style),
                )

            prev_tokens = total_tokens
            prev_cost = api_cost

        # Calculate overall trend
        if len(monthly_data) >= 2:
            first_cost = monthly_data[0]["total_cost"]
            last_cost = monthly_data[-1]["total_cost"]
            overall_change = last_cost - first_cost
            if first_cost > 0:
                overall_pct = (overall_change / first_cost) * 100
            else:
                overall_pct = 0

            trend_emoji = "📉" if overall_change < 0 else ("📈" if overall_change > 0 else "➡️")
            trend_style = "green" if overall_change < 0 else ("red" if overall_change > 0 else "white")

            lines.append("")

        # Create panel with table
        panel = Panel(
            Align.center(table),
            title="Month-over-Month",
            title_align="center",
            border_style=self.border_style,
            expand=False,
            padding=(1, 2),
        )

        return panel

    def create_no_data_display(self, view_type: str) -> Panel:
        """Create a display for when no data is available.

        Args:
            view_type: Type of view ('daily' or 'monthly')

        Returns:
            Rich Panel object
        """
        message = Text(
            f"No {view_type} data found.\n\nTry using Claude Code to generate some usage data.",
            style=self.warning_style,
            justify="center",
        )

        panel = Panel(
            Align.center(message, vertical="middle"),
            title=f"No {view_type.capitalize()} Data",
            title_align="center",
            border_style=self.warning_style,
            expand=True,
            height=10,
        )

        return panel

    def create_aggregate_table(
        self,
        aggregate_data: Union[List[Dict[str, Any]], List[Dict[str, Any]]],
        totals: Dict[str, Any],
        view_type: str,
        timezone: str = "UTC",
    ) -> Table:
        """Create a table for either daily or monthly aggregated data.

        Args:
            aggregate_data: List of aggregated data (daily or monthly)
            totals: Total statistics
            view_type: Type of view ('daily' or 'monthly')
            timezone: Timezone for display

        Returns:
            Rich Table object

        Raises:
            ValueError: If view_type is not 'daily' or 'monthly'
        """
        if view_type == "daily":
            return self.create_daily_table(aggregate_data, totals, timezone)
        elif view_type == "monthly":
            return self.create_monthly_table(aggregate_data, totals, timezone)
        else:
            raise ValueError(f"Invalid view type: {view_type}")

    def display_aggregated_view(
        self,
        data: List[Dict[str, Any]],
        view_mode: str,
        timezone: str,
        plan: str,
        token_limit: int,
        console: Optional[Console] = None,
    ) -> None:
        """Display aggregated view with table and summary.

        Args:
            data: Aggregated data
            view_mode: View type ('daily' or 'monthly')
            timezone: Timezone string
            plan: Plan type
            token_limit: Token limit for the plan
            console: Optional Console instance
        """
        if not data:
            no_data_display = self.create_no_data_display(view_mode)
            if console:
                console.print(no_data_display)
            else:
                print(no_data_display)
            return

        # Calculate totals
        totals = {
            "input_tokens": sum(d["input_tokens"] for d in data),
            "output_tokens": sum(d["output_tokens"] for d in data),
            "cache_creation_tokens": sum(d["cache_creation_tokens"] for d in data),
            "cache_read_tokens": sum(d["cache_read_tokens"] for d in data),
            "total_tokens": sum(
                d["input_tokens"]
                + d["output_tokens"]
                + d["cache_creation_tokens"]
                + d["cache_read_tokens"]
                for d in data
            ),
            "total_cost": sum(d["total_cost"] for d in data),
            "entries_count": sum(d.get("entries_count", 0) for d in data),
        }

        # Determine period and number of months for summary
        if view_mode == "daily":
            period = f"{data[0]['date']} to {data[-1]['date']}" if data else "No data"
            # Calculate approximate months from date range
            num_months = max(1, len(set(d["date"][:7] for d in data)))  # Count unique year-months
        else:  # monthly
            period = f"{data[0]['month']} to {data[-1]['month']}" if data else "No data"
            num_months = len(data)

        # Calculate data range string
        data_range = period  # Use the calculated period as the data range

        # Create and display summary panel with savings
        summary_panel = self.create_summary_panel(view_mode, totals, period, plan, num_months, data_range)

        # Create and display table
        table = self.create_aggregate_table(data, totals, view_mode, timezone)

        # Display using console if provided
        if console:
            console.print(summary_panel)
            console.print()
            console.print(table)
            # For monthly view, add month-over-month comparison
            if view_mode == "monthly" and len(data) > 1:
                console.print()
                mom_panel = self.create_month_over_month_panel(data, plan)
                console.print(mom_panel)
        else:
            from rich import print as rprint

            rprint(summary_panel)
            rprint()
            rprint(table)
            # For monthly view, add month-over-month comparison
            if view_mode == "monthly" and len(data) > 1:
                rprint()
                mom_panel = self.create_month_over_month_panel(data, plan)
                rprint(mom_panel)

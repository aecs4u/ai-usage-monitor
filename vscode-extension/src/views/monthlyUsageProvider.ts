import * as vscode from 'vscode';
import { CliManager, UsageData } from '../utils/cliManager';

export class MonthlyUsageProvider implements vscode.TreeDataProvider<MonthlyItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<MonthlyItem | undefined | null | void> = new vscode.EventEmitter<MonthlyItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<MonthlyItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private cliManager: CliManager) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: MonthlyItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: MonthlyItem): Promise<MonthlyItem[]> {
        if (!element) {
            // Root level - show all months
            const data = await this.cliManager.getMonthlyData();

            if (data.length === 0) {
                return [
                    new MonthlyItem(
                        'No Data',
                        'No monthly usage data available',
                        vscode.TreeItemCollapsibleState.None,
                        null
                    )
                ];
            }

            // Reverse to show most recent first
            return data.reverse().map(month => new MonthlyItem(
                this.cliManager.formatMonth(month.month || ''),
                `${this.cliManager.formatTokens(month.totalTokens)} tokens • ${this.cliManager.formatCost(month.totalCost)}`,
                vscode.TreeItemCollapsibleState.Collapsed,
                month
            ));
        } else if (element.data) {
            // Expanded month - show details
            const data = element.data;
            return [
                new MonthlyItem(
                    'Total Tokens',
                    this.cliManager.formatTokens(data.totalTokens),
                    vscode.TreeItemCollapsibleState.None,
                    null,
                    'symbol-number'
                ),
                new MonthlyItem(
                    'Total Cost',
                    this.cliManager.formatCost(data.totalCost),
                    vscode.TreeItemCollapsibleState.None,
                    null,
                    'currency-dollar'
                ),
                new MonthlyItem(
                    'Input Tokens',
                    this.cliManager.formatTokens(data.inputTokens),
                    vscode.TreeItemCollapsibleState.None,
                    null,
                    'arrow-right'
                ),
                new MonthlyItem(
                    'Output Tokens',
                    this.cliManager.formatTokens(data.outputTokens),
                    vscode.TreeItemCollapsibleState.None,
                    null,
                    'arrow-left'
                ),
                new MonthlyItem(
                    'Cache Created',
                    this.cliManager.formatTokens(data.cacheCreationTokens),
                    vscode.TreeItemCollapsibleState.None,
                    null,
                    'database'
                ),
                new MonthlyItem(
                    'Cache Read',
                    this.cliManager.formatTokens(data.cacheReadTokens),
                    vscode.TreeItemCollapsibleState.None,
                    null,
                    'dash'
                ),
                new MonthlyItem(
                    'Total Sessions',
                    data.entriesCount.toString(),
                    vscode.TreeItemCollapsibleState.None,
                    null,
                    'list-unordered'
                )
            ];
        }

        return [];
    }
}

class MonthlyItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly description: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly data: UsageData | null,
        public readonly iconName?: string
    ) {
        super(label, collapsibleState);

        this.description = description;
        this.tooltip = `${label}: ${description}`;

        if (iconName) {
            this.iconPath = new vscode.ThemeIcon(iconName);
        } else if (data) {
            this.iconPath = new vscode.ThemeIcon('calendar');
        }
    }

    contextValue = 'monthlyItem';
}

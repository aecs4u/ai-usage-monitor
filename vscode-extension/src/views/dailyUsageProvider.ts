import * as vscode from 'vscode';
import { CliManager, UsageData } from '../utils/cliManager';

export class DailyUsageProvider implements vscode.TreeDataProvider<DailyItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<DailyItem | undefined | null | void> = new vscode.EventEmitter<DailyItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<DailyItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private cliManager: CliManager) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: DailyItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: DailyItem): Promise<DailyItem[]> {
        if (!element) {
            // Root level - show last 7 days
            const data = await this.cliManager.getDailyData();

            if (data.length === 0) {
                return [
                    new DailyItem(
                        'No Data',
                        'No daily usage data available',
                        vscode.TreeItemCollapsibleState.None,
                        null
                    )
                ];
            }

            // Get last 7 days
            const recent = data.slice(-7).reverse();

            return recent.map(day => new DailyItem(
                this.cliManager.formatDate(day.date || ''),
                `${this.cliManager.formatTokens(day.totalTokens)} tokens • ${this.cliManager.formatCost(day.totalCost)}`,
                vscode.TreeItemCollapsibleState.Collapsed,
                day
            ));
        } else if (element.data) {
            // Expanded day - show details
            const data = element.data;
            return [
                new DailyItem(
                    'Total Tokens',
                    this.cliManager.formatTokens(data.totalTokens),
                    vscode.TreeItemCollapsibleState.None,
                    null,
                    'symbol-number'
                ),
                new DailyItem(
                    'Cost',
                    this.cliManager.formatCost(data.totalCost),
                    vscode.TreeItemCollapsibleState.None,
                    null,
                    'currency-dollar'
                ),
                new DailyItem(
                    'Input',
                    this.cliManager.formatTokens(data.inputTokens),
                    vscode.TreeItemCollapsibleState.None,
                    null,
                    'arrow-right'
                ),
                new DailyItem(
                    'Output',
                    this.cliManager.formatTokens(data.outputTokens),
                    vscode.TreeItemCollapsibleState.None,
                    null,
                    'arrow-left'
                ),
                new DailyItem(
                    'Cache Created',
                    this.cliManager.formatTokens(data.cacheCreationTokens),
                    vscode.TreeItemCollapsibleState.None,
                    null,
                    'database'
                ),
                new DailyItem(
                    'Cache Read',
                    this.cliManager.formatTokens(data.cacheReadTokens),
                    vscode.TreeItemCollapsibleState.None,
                    null,
                    'dash'
                ),
                new DailyItem(
                    'Sessions',
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

class DailyItem extends vscode.TreeItem {
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

    contextValue = 'dailyItem';
}

import * as vscode from 'vscode';
import { CliManager } from '../utils/cliManager';

export class OverviewProvider implements vscode.TreeDataProvider<OverviewItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<OverviewItem | undefined | null | void> = new vscode.EventEmitter<OverviewItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<OverviewItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private cliManager: CliManager) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: OverviewItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: OverviewItem): Promise<OverviewItem[]> {
        if (!element) {
            // Root level
            const isAvailable = await this.cliManager.checkCliAvailable();

            if (!isAvailable) {
                return [
                    new OverviewItem(
                        'CLI Not Found',
                        'ai-usage-monitor CLI not found. Install it with: pip install ai-usage-monitor',
                        vscode.TreeItemCollapsibleState.None,
                        'warning'
                    )
                ];
            }

            const data = await this.cliManager.getOverviewData();

            if (!data) {
                return [
                    new OverviewItem(
                        'No Data Available',
                        'No usage data found. Use an AI coding assistant to generate data.',
                        vscode.TreeItemCollapsibleState.None,
                        'info'
                    )
                ];
            }

            return [
                new OverviewItem(
                    'Current Month',
                    this.cliManager.formatMonth(data.month || ''),
                    vscode.TreeItemCollapsibleState.Expanded,
                    'calendar'
                ),
                new OverviewItem(
                    'Total Tokens',
                    this.cliManager.formatTokens(data.totalTokens),
                    vscode.TreeItemCollapsibleState.None,
                    'symbol-number',
                    data
                ),
                new OverviewItem(
                    'Total Cost',
                    this.cliManager.formatCost(data.totalCost),
                    vscode.TreeItemCollapsibleState.None,
                    'currency-dollar',
                    data
                ),
                new OverviewItem(
                    'Input Tokens',
                    this.cliManager.formatTokens(data.inputTokens),
                    vscode.TreeItemCollapsibleState.None,
                    'arrow-right',
                    data
                ),
                new OverviewItem(
                    'Output Tokens',
                    this.cliManager.formatTokens(data.outputTokens),
                    vscode.TreeItemCollapsibleState.None,
                    'arrow-left',
                    data
                ),
                new OverviewItem(
                    'Cache Created',
                    this.cliManager.formatTokens(data.cacheCreationTokens),
                    vscode.TreeItemCollapsibleState.None,
                    'database',
                    data
                ),
                new OverviewItem(
                    'Cache Read',
                    this.cliManager.formatTokens(data.cacheReadTokens),
                    vscode.TreeItemCollapsibleState.None,
                    'dash',
                    data
                ),
                new OverviewItem(
                    'Sessions',
                    data.entriesCount.toString(),
                    vscode.TreeItemCollapsibleState.None,
                    'list-unordered',
                    data
                )
            ];
        }

        return [];
    }
}

class OverviewItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly description: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly iconName?: string,
        public readonly data?: any
    ) {
        super(label, collapsibleState);

        this.description = description;
        this.tooltip = `${label}: ${description}`;

        if (iconName) {
            this.iconPath = new vscode.ThemeIcon(iconName);
        }
    }

    contextValue = 'overviewItem';
}

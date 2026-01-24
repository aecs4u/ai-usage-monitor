import * as vscode from 'vscode';
import { CliManager, ToolInfo } from '../utils/cliManager';

export class ToolsProvider implements vscode.TreeDataProvider<ToolItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<ToolItem | undefined | null | void> = new vscode.EventEmitter<ToolItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<ToolItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private cliManager: CliManager) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: ToolItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: ToolItem): Promise<ToolItem[]> {
        if (!element) {
            const tools = await this.cliManager.getAvailableTools();

            if (tools.length === 0) {
                return [
                    new ToolItem(
                        'No Tools',
                        'No AI tools detected',
                        false,
                        vscode.TreeItemCollapsibleState.None
                    )
                ];
            }

            return tools.map(tool => new ToolItem(
                tool.displayName,
                tool.available ? 'Available' : 'Not detected',
                tool.available,
                vscode.TreeItemCollapsibleState.None,
                tool.name
            ));
        }

        return [];
    }
}

class ToolItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly description: string,
        public readonly available: boolean,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly toolName?: string
    ) {
        super(label, collapsibleState);

        this.description = description;
        this.tooltip = `${label}: ${description}`;

        if (available) {
            this.iconPath = new vscode.ThemeIcon('check', new vscode.ThemeColor('testing.iconPassed'));
        } else {
            this.iconPath = new vscode.ThemeIcon('circle-outline', new vscode.ThemeColor('testing.iconQueued'));
        }

        if (toolName) {
            this.command = {
                command: 'aiUsageMonitor.selectTool',
                title: 'Select Tool',
                arguments: [toolName]
            };
        }
    }

    contextValue = 'toolItem';
}

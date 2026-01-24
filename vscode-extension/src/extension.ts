import * as vscode from 'vscode';
import { OverviewProvider } from './views/overviewProvider';
import { DailyUsageProvider } from './views/dailyUsageProvider';
import { MonthlyUsageProvider } from './views/monthlyUsageProvider';
import { ToolsProvider } from './views/toolsProvider';
import { DashboardPanel } from './webviews/dashboardPanel';
import { CostAnalysisPanel } from './webviews/costAnalysisPanel';
import { CliManager } from './utils/cliManager';

export function activate(context: vscode.ExtensionContext) {
    console.log('AI Usage Monitor extension is now active');

    // Initialize CLI manager
    const cliManager = new CliManager();

    // Create tree data providers
    const overviewProvider = new OverviewProvider(cliManager);
    const dailyProvider = new DailyUsageProvider(cliManager);
    const monthlyProvider = new MonthlyUsageProvider(cliManager);
    const toolsProvider = new ToolsProvider(cliManager);

    // Register tree views
    const overviewTree = vscode.window.createTreeView('aiUsageOverview', {
        treeDataProvider: overviewProvider,
        showCollapseAll: true
    });

    const dailyTree = vscode.window.createTreeView('aiUsageDaily', {
        treeDataProvider: dailyProvider,
        showCollapseAll: true
    });

    const monthlyTree = vscode.window.createTreeView('aiUsageMonthly', {
        treeDataProvider: monthlyProvider,
        showCollapseAll: true
    });

    const toolsTree = vscode.window.createTreeView('aiUsageTools', {
        treeDataProvider: toolsProvider,
        showCollapseAll: false
    });

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('aiUsageMonitor.refresh', async () => {
            await refreshAllViews();
            vscode.window.showInformationMessage('AI usage data refreshed');
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('aiUsageMonitor.showDashboard', () => {
            DashboardPanel.createOrShow(context.extensionUri, cliManager);
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('aiUsageMonitor.exportData', async () => {
            const format = await vscode.window.showQuickPick(['JSON', 'CSV'], {
                placeHolder: 'Select export format'
            });

            if (!format) {
                return;
            }

            const uri = await vscode.window.showSaveDialog({
                filters: {
                    'JSON': ['json'],
                    'CSV': ['csv']
                },
                defaultUri: vscode.Uri.file(`ai-usage-export.${format.toLowerCase()}`)
            });

            if (uri) {
                try {
                    await cliManager.exportData(format.toLowerCase(), uri.fsPath);
                    vscode.window.showInformationMessage(`Data exported to ${uri.fsPath}`);
                } catch (error) {
                    vscode.window.showErrorMessage(`Export failed: ${error}`);
                }
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('aiUsageMonitor.showCosts', () => {
            CostAnalysisPanel.createOrShow(context.extensionUri, cliManager);
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('aiUsageMonitor.configure', () => {
            vscode.commands.executeCommand('workbench.action.openSettings', 'aiUsageMonitor');
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('aiUsageMonitor.selectTool', async () => {
            const tools = [
                { label: 'Auto Detect', value: 'auto' },
                { label: 'All Tools', value: 'all' },
                { label: 'Claude Code', value: 'claude-code' },
                { label: 'Cline', value: 'cline' },
                { label: 'Codex CLI', value: 'codex-cli' },
                { label: 'Gemini CLI', value: 'gemini-cli' },
                { label: 'GitHub Copilot', value: 'github-copilot' },
                { label: 'Roo Code', value: 'roo-code' },
                { label: 'Kilo Code', value: 'kilo-code' },
                { label: 'OpenCode', value: 'opencode' },
                { label: 'Pi Agent', value: 'pi-agent' }
            ];

            const selected = await vscode.window.showQuickPick(tools, {
                placeHolder: 'Select AI tool to monitor'
            });

            if (selected) {
                const config = vscode.workspace.getConfiguration('aiUsageMonitor');
                await config.update('defaultTool', selected.value, vscode.ConfigurationTarget.Global);
                await refreshAllViews();
                vscode.window.showInformationMessage(`Monitoring: ${selected.label}`);
            }
        })
    );

    // Auto-refresh timer
    let refreshTimer: NodeJS.Timeout | undefined;

    const setupAutoRefresh = () => {
        if (refreshTimer) {
            clearInterval(refreshTimer);
        }

        const config = vscode.workspace.getConfiguration('aiUsageMonitor');
        const enabled = config.get<boolean>('enableAutoRefresh', true);
        const interval = config.get<number>('refreshInterval', 60) * 1000;

        if (enabled) {
            refreshTimer = setInterval(() => {
                refreshAllViews();
            }, interval);
        }
    };

    setupAutoRefresh();

    // Watch for configuration changes
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('aiUsageMonitor')) {
                setupAutoRefresh();
                refreshAllViews();
            }
        })
    );

    // Helper function to refresh all views
    async function refreshAllViews() {
        overviewProvider.refresh();
        dailyProvider.refresh();
        monthlyProvider.refresh();
        toolsProvider.refresh();
    }

    // Initial data load
    refreshAllViews();

    // Add subscriptions to context
    context.subscriptions.push(
        overviewTree,
        dailyTree,
        monthlyTree,
        toolsTree
    );

    // Cleanup on deactivate
    context.subscriptions.push({
        dispose: () => {
            if (refreshTimer) {
                clearInterval(refreshTimer);
            }
        }
    });

    console.log('AI Usage Monitor extension fully initialized');
}

export function deactivate() {
    console.log('AI Usage Monitor extension deactivated');
}

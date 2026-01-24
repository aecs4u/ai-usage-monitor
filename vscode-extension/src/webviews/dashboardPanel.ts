import * as vscode from 'vscode';
import { CliManager } from '../utils/cliManager';

export class DashboardPanel {
    public static currentPanel: DashboardPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];

    public static createOrShow(extensionUri: vscode.Uri, cliManager: CliManager) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (DashboardPanel.currentPanel) {
            DashboardPanel.currentPanel._panel.reveal(column);
            DashboardPanel.currentPanel.update(cliManager);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            'aiUsageDashboard',
            'AI Usage Dashboard',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [extensionUri]
            }
        );

        DashboardPanel.currentPanel = new DashboardPanel(panel, extensionUri, cliManager);
    }

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri, cliManager: CliManager) {
        this._panel = panel;
        this._extensionUri = extensionUri;

        this.update(cliManager);

        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        this._panel.webview.onDidReceiveMessage(
            async message => {
                switch (message.command) {
                    case 'refresh':
                        await this.update(cliManager);
                        break;
                }
            },
            null,
            this._disposables
        );
    }

    private async update(cliManager: CliManager) {
        const webview = this._panel.webview;

        this._panel.title = 'AI Usage Dashboard';
        this._panel.webview.html = await this._getHtmlForWebview(webview, cliManager);
    }

    private async _getHtmlForWebview(webview: vscode.Webview, cliManager: CliManager) {
        const dailyData = await cliManager.getDailyData();
        const monthlyData = await cliManager.getMonthlyData();

        // Prepare data for charts
        const dailyLabels = dailyData.slice(-14).map(d => cliManager.formatDate(d.date || ''));
        const dailyTokens = dailyData.slice(-14).map(d => d.totalTokens);
        const dailyCosts = dailyData.slice(-14).map(d => d.totalCost);

        const monthlyLabels = monthlyData.map(m => cliManager.formatMonth(m.month || ''));
        const monthlyTokens = monthlyData.map(m => m.totalTokens);
        const monthlyCosts = monthlyData.map(m => m.totalCost);

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Usage Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {
            padding: 20px;
            color: var(--vscode-foreground);
            font-family: var(--vscode-font-family);
        }
        .dashboard-header {
            margin-bottom: 30px;
        }
        .dashboard-header h1 {
            margin: 0 0 10px 0;
            color: var(--vscode-foreground);
        }
        .refresh-button {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 8px 16px;
            cursor: pointer;
            border-radius: 2px;
        }
        .refresh-button:hover {
            background: var(--vscode-button-hoverBackground);
        }
        .chart-container {
            margin-bottom: 40px;
            background: var(--vscode-editor-background);
            padding: 20px;
            border-radius: 4px;
        }
        .chart-container h2 {
            margin-top: 0;
            color: var(--vscode-foreground);
        }
        canvas {
            max-height: 300px;
        }
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1>📊 AI Usage Dashboard</h1>
        <button class="refresh-button" onclick="refresh()">🔄 Refresh</button>
    </div>

    <div class="chart-container">
        <h2>Daily Token Usage (Last 14 Days)</h2>
        <canvas id="dailyTokensChart"></canvas>
    </div>

    <div class="chart-container">
        <h2>Daily Costs (Last 14 Days)</h2>
        <canvas id="dailyCostsChart"></canvas>
    </div>

    <div class="chart-container">
        <h2>Monthly Token Usage</h2>
        <canvas id="monthlyTokensChart"></canvas>
    </div>

    <div class="chart-container">
        <h2>Monthly Costs</h2>
        <canvas id="monthlyCostsChart"></canvas>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        const chartOptions = {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: {
                        color: getComputedStyle(document.body).getPropertyValue('--vscode-foreground')
                    }
                }
            },
            scales: {
                y: {
                    ticks: {
                        color: getComputedStyle(document.body).getPropertyValue('--vscode-foreground')
                    },
                    grid: {
                        color: getComputedStyle(document.body).getPropertyValue('--vscode-editorWidget-border')
                    }
                },
                x: {
                    ticks: {
                        color: getComputedStyle(document.body).getPropertyValue('--vscode-foreground')
                    },
                    grid: {
                        color: getComputedStyle(document.body).getPropertyValue('--vscode-editorWidget-border')
                    }
                }
            }
        };

        // Daily Tokens Chart
        new Chart(document.getElementById('dailyTokensChart'), {
            type: 'line',
            data: {
                labels: ${JSON.stringify(dailyLabels)},
                datasets: [{
                    label: 'Total Tokens',
                    data: ${JSON.stringify(dailyTokens)},
                    borderColor: '#007acc',
                    backgroundColor: 'rgba(0, 122, 204, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: chartOptions
        });

        // Daily Costs Chart
        new Chart(document.getElementById('dailyCostsChart'), {
            type: 'bar',
            data: {
                labels: ${JSON.stringify(dailyLabels)},
                datasets: [{
                    label: 'Cost ($)',
                    data: ${JSON.stringify(dailyCosts)},
                    backgroundColor: '#22c55e',
                    borderColor: '#16a34a',
                    borderWidth: 1
                }]
            },
            options: chartOptions
        });

        // Monthly Tokens Chart
        new Chart(document.getElementById('monthlyTokensChart'), {
            type: 'bar',
            data: {
                labels: ${JSON.stringify(monthlyLabels)},
                datasets: [{
                    label: 'Total Tokens',
                    data: ${JSON.stringify(monthlyTokens)},
                    backgroundColor: '#8b5cf6',
                    borderColor: '#7c3aed',
                    borderWidth: 1
                }]
            },
            options: chartOptions
        });

        // Monthly Costs Chart
        new Chart(document.getElementById('monthlyCostsChart'), {
            type: 'line',
            data: {
                labels: ${JSON.stringify(monthlyLabels)},
                datasets: [{
                    label: 'Cost ($)',
                    data: ${JSON.stringify(monthlyCosts)},
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: chartOptions
        });

        function refresh() {
            vscode.postMessage({ command: 'refresh' });
        }
    </script>
</body>
</html>`;
    }

    public dispose() {
        DashboardPanel.currentPanel = undefined;

        this._panel.dispose();

        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}

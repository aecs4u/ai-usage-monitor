import * as vscode from 'vscode';
import { CliManager } from '../utils/cliManager';

export class CostAnalysisPanel {
    public static currentPanel: CostAnalysisPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];

    public static createOrShow(extensionUri: vscode.Uri, cliManager: CliManager) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (CostAnalysisPanel.currentPanel) {
            CostAnalysisPanel.currentPanel._panel.reveal(column);
            CostAnalysisPanel.currentPanel.update(cliManager);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            'aiCostAnalysis',
            'Cost Analysis',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [extensionUri]
            }
        );

        CostAnalysisPanel.currentPanel = new CostAnalysisPanel(panel, extensionUri, cliManager);
    }

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri, cliManager: CliManager) {
        this._panel = panel;
        this._extensionUri = extensionUri;

        this.update(cliManager);

        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
    }

    private async update(cliManager: CliManager) {
        const webview = this._panel.webview;

        this._panel.title = 'Cost Analysis';
        this._panel.webview.html = await this._getHtmlForWebview(webview, cliManager);
    }

    private async _getHtmlForWebview(webview: vscode.Webview, cliManager: CliManager) {
        const monthlyData = await cliManager.getMonthlyData();

        // Calculate cost analysis
        let totalCost = 0;
        let avgMonthlyCost = 0;
        let currentMonthCost = 0;

        if (monthlyData.length > 0) {
            totalCost = monthlyData.reduce((sum, m) => sum + m.totalCost, 0);
            avgMonthlyCost = totalCost / monthlyData.length;
            currentMonthCost = monthlyData[monthlyData.length - 1].totalCost;
        }

        // Subscription recommendations
        const plans = [
            { name: 'API Only', monthlyFee: 0, includesTokens: 0 },
            { name: 'Max5', monthlyFee: 20, description: '$20/month subscription' },
            { name: 'Max20', monthlyFee: 60, description: '$60/month subscription' }
        ];

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cost Analysis</title>
    <style>
        body {
            padding: 20px;
            color: var(--vscode-foreground);
            font-family: var(--vscode-font-family);
        }
        .header {
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0 0 10px 0;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: var(--vscode-editor-background);
            padding: 20px;
            border-radius: 4px;
            border-left: 4px solid #007acc;
        }
        .metric-card h3 {
            margin: 0 0 10px 0;
            font-size: 14px;
            color: var(--vscode-descriptionForeground);
        }
        .metric-card .value {
            font-size: 28px;
            font-weight: bold;
            color: var(--vscode-foreground);
        }
        .metric-card .subtext {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            margin-top: 5px;
        }
        .recommendations {
            background: var(--vscode-editor-background);
            padding: 20px;
            border-radius: 4px;
            margin-bottom: 30px;
        }
        .recommendations h2 {
            margin-top: 0;
        }
        .plan {
            padding: 15px;
            margin: 10px 0;
            background: var(--vscode-input-background);
            border-radius: 4px;
            border: 1px solid var(--vscode-editorWidget-border);
        }
        .plan h3 {
            margin: 0 0 10px 0;
        }
        .plan .savings {
            color: #22c55e;
            font-weight: bold;
        }
        .plan .cost-more {
            color: #ef4444;
            font-weight: bold;
        }
        .insights {
            background: var(--vscode-editor-background);
            padding: 20px;
            border-radius: 4px;
        }
        .insights h2 {
            margin-top: 0;
        }
        .insight-item {
            padding: 10px 0;
            border-bottom: 1px solid var(--vscode-editorWidget-border);
        }
        .insight-item:last-child {
            border-bottom: none;
        }
        .insight-item .icon {
            display: inline-block;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>💰 Cost Analysis</h1>
        <p>Detailed breakdown of your AI usage costs and recommendations</p>
    </div>

    <div class="metrics">
        <div class="metric-card">
            <h3>Total Spend</h3>
            <div class="value">$${totalCost.toFixed(2)}</div>
            <div class="subtext">All time</div>
        </div>

        <div class="metric-card">
            <h3>Average Monthly</h3>
            <div class="value">$${avgMonthlyCost.toFixed(2)}</div>
            <div class="subtext">${monthlyData.length} months tracked</div>
        </div>

        <div class="metric-card">
            <h3>Current Month</h3>
            <div class="value">$${currentMonthCost.toFixed(2)}</div>
            <div class="subtext">${currentMonthCost > avgMonthlyCost ? '↑ Above' : '↓ Below'} average</div>
        </div>
    </div>

    <div class="recommendations">
        <h2>Subscription Recommendations</h2>
        <p>Based on your average monthly spend of $${avgMonthlyCost.toFixed(2)}:</p>

        <div class="plan">
            <h3>API Only (Current)</h3>
            <p>Pay as you go: $${avgMonthlyCost.toFixed(2)}/month average</p>
            <p>Best for: Variable usage patterns</p>
        </div>

        <div class="plan">
            <h3>Max5 Plan ($20/month)</h3>
            ${avgMonthlyCost > 20
                ? `<p class="savings">💰 Save $${(avgMonthlyCost - 20).toFixed(2)}/month</p>`
                : `<p class="cost-more">Costs $${(20 - avgMonthlyCost).toFixed(2)}/month more</p>`}
            <p>Best for: Regular daily usage</p>
        </div>

        <div class="plan">
            <h3>Max20 Plan ($60/month)</h3>
            ${avgMonthlyCost > 60
                ? `<p class="savings">💰 Save $${(avgMonthlyCost - 60).toFixed(2)}/month</p>`
                : `<p class="cost-more">Costs $${(60 - avgMonthlyCost).toFixed(2)}/month more</p>`}
            <p>Best for: Heavy daily usage</p>
        </div>
    </div>

    <div class="insights">
        <h2>💡 Insights</h2>

        <div class="insight-item">
            <span class="icon">📊</span>
            <strong>Usage Trend:</strong> ${currentMonthCost > avgMonthlyCost ? 'Increasing' : 'Stable or decreasing'}
        </div>

        <div class="insight-item">
            <span class="icon">💵</span>
            <strong>Cost Efficiency:</strong> ${avgMonthlyCost < 20 ? 'API is most cost-effective' : avgMonthlyCost < 60 ? 'Consider Max5 plan' : 'Max20 plan recommended'}
        </div>

        <div class="insight-item">
            <span class="icon">📈</span>
            <strong>Projection:</strong> At current rate, next month will cost ~$${currentMonthCost.toFixed(2)}
        </div>

        <div class="insight-item">
            <span class="icon">🎯</span>
            <strong>Recommendation:</strong> ${
                avgMonthlyCost > 60 ? 'Upgrade to Max20 for significant savings' :
                avgMonthlyCost > 20 ? 'Max5 plan offers good value for your usage' :
                'API pricing is optimal for your current usage level'
            }
        </div>
    </div>
</body>
</html>`;
    }

    public dispose() {
        CostAnalysisPanel.currentPanel = undefined;

        this._panel.dispose();

        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}

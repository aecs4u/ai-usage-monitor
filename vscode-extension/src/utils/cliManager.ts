import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export interface UsageData {
    tool: string;
    inputTokens: number;
    outputTokens: number;
    cacheCreationTokens: number;
    cacheReadTokens: number;
    totalTokens: number;
    totalCost: number;
    entriesCount: number;
    date?: string;
    month?: string;
}

export interface ToolInfo {
    name: string;
    displayName: string;
    available: boolean;
}

export class CliManager {
    private cliPath: string;

    constructor() {
        this.cliPath = this.getCliPath();
    }

    private getCliPath(): string {
        const config = vscode.workspace.getConfiguration('aiUsageMonitor');
        const customPath = config.get<string>('cliPath', '');

        if (customPath) {
            return customPath;
        }

        // Default to 'ai-usage-monitor' in PATH
        return 'ai-usage-monitor';
    }

    private getDefaultTool(): string {
        const config = vscode.workspace.getConfiguration('aiUsageMonitor');
        return config.get<string>('defaultTool', 'auto');
    }

    async checkCliAvailable(): Promise<boolean> {
        try {
            await execAsync(`${this.cliPath} --version`);
            return true;
        } catch (error) {
            return false;
        }
    }

    async getOverviewData(): Promise<UsageData | null> {
        try {
            const tool = this.getDefaultTool();
            const cmd = `${this.cliPath} --tool ${tool} --view monthly --export json`;
            const { stdout } = await execAsync(cmd);
            const data = JSON.parse(stdout);

            if (data.data && data.data.length > 0) {
                // Get the most recent month
                return data.data[data.data.length - 1];
            }

            return null;
        } catch (error) {
            console.error('Failed to get overview data:', error);
            return null;
        }
    }

    async getDailyData(): Promise<UsageData[]> {
        try {
            const tool = this.getDefaultTool();
            const cmd = `${this.cliPath} --tool ${tool} --view daily --export json`;
            const { stdout } = await execAsync(cmd);
            const data = JSON.parse(stdout);

            return data.data || [];
        } catch (error) {
            console.error('Failed to get daily data:', error);
            return [];
        }
    }

    async getMonthlyData(): Promise<UsageData[]> {
        try {
            const tool = this.getDefaultTool();
            const cmd = `${this.cliPath} --tool ${tool} --view monthly --export json`;
            const { stdout } = await execAsync(cmd);
            const data = JSON.parse(stdout);

            return data.data || [];
        } catch (error) {
            console.error('Failed to get monthly data:', error);
            return [];
        }
    }

    async getAvailableTools(): Promise<ToolInfo[]> {
        // Tool information
        const allTools: ToolInfo[] = [
            { name: 'claude-code', displayName: 'Claude Code', available: false },
            { name: 'cline', displayName: 'Cline', available: false },
            { name: 'codex-cli', displayName: 'Codex CLI', available: false },
            { name: 'gemini-cli', displayName: 'Gemini CLI', available: false },
            { name: 'github-copilot', displayName: 'GitHub Copilot', available: false },
            { name: 'roo-code', displayName: 'Roo Code', available: false },
            { name: 'kilo-code', displayName: 'Kilo Code', available: false },
            { name: 'opencode', displayName: 'OpenCode', available: false },
            { name: 'pi-agent', displayName: 'Pi Agent', available: false }
        ];

        // Check each tool
        for (const tool of allTools) {
            try {
                const cmd = `${this.cliPath} --tool ${tool.name} --view monthly --export json`;
                const { stdout } = await execAsync(cmd);
                const data = JSON.parse(stdout);
                tool.available = data.data && data.data.length > 0;
            } catch (error) {
                tool.available = false;
            }
        }

        return allTools;
    }

    async exportData(format: string, outputPath: string): Promise<void> {
        const tool = this.getDefaultTool();
        const cmd = `${this.cliPath} --tool ${tool} --view monthly --export ${format} --export-path "${outputPath}"`;
        await execAsync(cmd);
    }

    formatTokens(tokens: number): string {
        if (tokens >= 1000000) {
            return `${(tokens / 1000000).toFixed(2)}M`;
        } else if (tokens >= 1000) {
            return `${(tokens / 1000).toFixed(2)}K`;
        }
        return tokens.toString();
    }

    formatCost(cost: number): string {
        return `$${cost.toFixed(2)}`;
    }

    formatDate(dateStr: string): string {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    }

    formatMonth(monthStr: string): string {
        const date = new Date(monthStr + '-01');
        return date.toLocaleDateString('en-US', {
            month: 'long',
            year: 'numeric'
        });
    }
}

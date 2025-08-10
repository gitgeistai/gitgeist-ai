"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.GitgeistProvider = void 0;
const vscode = require("vscode");
class GitgeistProvider {
    constructor() {
        this.config = vscode.workspace.getConfiguration('gitgeist');
    }
    async generateCommitMessage() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            throw new Error('No workspace folder found');
        }
        // Execute gitgeist command
        const { exec } = require('child_process');
        const { promisify } = require('util');
        const execAsync = promisify(exec);
        try {
            const { stdout } = await execAsync('gitgeist commit --dry-run', {
                cwd: workspaceFolder.uri.fsPath
            });
            // Parse output to extract commit message
            const lines = stdout.split('\n');
            const messageIndex = lines.findIndex(line => line.includes('Generated commit message:'));
            if (messageIndex !== -1 && messageIndex + 1 < lines.length) {
                return lines[messageIndex + 1].trim();
            }
            return null;
        }
        catch (error) {
            throw new Error(`Gitgeist command failed: ${error}`);
        }
    }
    async analyzeChanges() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            throw new Error('No workspace folder found');
        }
        const { exec } = require('child_process');
        const { promisify } = require('util');
        const execAsync = promisify(exec);
        try {
            const { stdout } = await execAsync('gitgeist analyze', {
                cwd: workspaceFolder.uri.fsPath
            });
            // Parse analysis output
            return { output: stdout };
        }
        catch (error) {
            throw new Error(`Analysis failed: ${error}`);
        }
    }
}
exports.GitgeistProvider = GitgeistProvider;
//# sourceMappingURL=gitgeistProvider.js.map
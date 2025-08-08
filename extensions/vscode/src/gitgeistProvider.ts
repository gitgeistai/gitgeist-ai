import * as vscode from 'vscode';
import axios from 'axios';

export class GitgeistProvider {
    private config = vscode.workspace.getConfiguration('gitgeist');

    async generateCommitMessage(): Promise<string | null> {
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
        } catch (error) {
            throw new Error(`Gitgeist command failed: ${error}`);
        }
    }

    async analyzeChanges(): Promise<any> {
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
        } catch (error) {
            throw new Error(`Analysis failed: ${error}`);
        }
    }
}
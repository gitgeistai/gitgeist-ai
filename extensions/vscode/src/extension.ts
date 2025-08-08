import * as vscode from 'vscode';
import { GitgeistProvider } from './gitgeistProvider';

export function activate(context: vscode.ExtensionContext) {
    const provider = new GitgeistProvider();

    const generateCommitCommand = vscode.commands.registerCommand('gitgeist.generateCommit', async () => {
        try {
            const message = await provider.generateCommitMessage();
            if (message) {
                const gitExtension = vscode.extensions.getExtension('vscode.git')?.exports;
                const git = gitExtension?.getAPI(1);
                
                if (git && git.repositories.length > 0) {
                    git.repositories[0].inputBox.value = message;
                    vscode.window.showInformationMessage('✅ Commit message generated!');
                }
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to generate commit: ${error}`);
        }
    });

    context.subscriptions.push(generateCommitCommand);
}

export function deactivate() {}
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = require("vscode");
const child_process_1 = require("child_process");
const util_1 = require("util");
const execAsync = (0, util_1.promisify)(child_process_1.exec);
function activate(context) {
    console.log('🧠 Gitgeist extension activated!');
    // Register commands
    const commands = [
        vscode.commands.registerCommand('gitgeist.generateCommit', generateCommitMessage),
        vscode.commands.registerCommand('gitgeist.quickCommit', quickCommit),
        vscode.commands.registerCommand('gitgeist.analyzeChanges', analyzeChanges),
        vscode.commands.registerCommand('gitgeist.openSettings', openSettings)
    ];
    context.subscriptions.push(...commands);
    // Show welcome message on first activation
    const hasShownWelcome = context.globalState.get('gitgeist.hasShownWelcome', false);
    if (!hasShownWelcome) {
        showWelcomeMessage(context);
    }
}
exports.activate = activate;
async function showWelcomeMessage(context) {
    const action = await vscode.window.showInformationMessage('🧠 Welcome to Gitgeist! AI-powered Git commit generation is now available.', 'Get Started', 'View Documentation', 'Don\'t Show Again');
    if (action === 'Get Started') {
        vscode.commands.executeCommand('gitgeist.generateCommit');
    }
    else if (action === 'View Documentation') {
        vscode.env.openExternal(vscode.Uri.parse('https://github.com/gitgeistai/gitgeist-ai'));
    }
    if (action === 'Don\'t Show Again' || action) {
        context.globalState.update('gitgeist.hasShownWelcome', true);
    }
}
async function generateCommitMessage() {
    const workspaceFolder = getWorkspaceFolder();
    if (!workspaceFolder)
        return;
    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "🧠 Generating AI commit message...",
        cancellable: false
    }, async (progress) => {
        try {
            progress.report({ message: "Checking installation..." });
            await checkGitgeistInstallation(workspaceFolder.uri.fsPath);
            progress.report({ message: "Analyzing changes..." });
            const { stdout } = await execAsync('gitgeist commit --dry-run', {
                cwd: workspaceFolder.uri.fsPath
            });
            const commitMessage = extractCommitMessage(stdout);
            if (commitMessage) {
                await showCommitDialog(commitMessage, workspaceFolder.uri.fsPath);
            }
            else {
                vscode.window.showErrorMessage('Failed to generate commit message');
            }
        }
        catch (error) {
            handleError(error);
        }
    });
}
async function quickCommit() {
    const workspaceFolder = getWorkspaceFolder();
    if (!workspaceFolder)
        return;
    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "⚡ Quick AI commit...",
        cancellable: false
    }, async (progress) => {
        try {
            progress.report({ message: "Generating and committing..." });
            await execAsync('gitgeist commit --auto', {
                cwd: workspaceFolder.uri.fsPath
            });
            vscode.window.showInformationMessage('✅ Quick commit created successfully!');
        }
        catch (error) {
            handleError(error);
        }
    });
}
async function analyzeChanges() {
    const workspaceFolder = getWorkspaceFolder();
    if (!workspaceFolder)
        return;
    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "🔍 Analyzing repository changes...",
        cancellable: false
    }, async (progress) => {
        try {
            const { stdout } = await execAsync('gitgeist analyze', {
                cwd: workspaceFolder.uri.fsPath
            });
            const outputChannel = vscode.window.createOutputChannel('Gitgeist Analysis');
            outputChannel.clear();
            outputChannel.appendLine('🔍 Gitgeist Repository Analysis');
            outputChannel.appendLine('================================\n');
            outputChannel.appendLine(stdout);
            outputChannel.show();
        }
        catch (error) {
            handleError(error);
        }
    });
}
function openSettings() {
    vscode.commands.executeCommand('workbench.action.openSettings', 'gitgeist');
}
// Helper functions
function getWorkspaceFolder() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder found');
        return undefined;
    }
    return workspaceFolder;
}
async function checkGitgeistInstallation(cwd) {
    try {
        await execAsync('gitgeist --version', { cwd });
    }
    catch (error) {
        const action = await vscode.window.showErrorMessage('Gitgeist not found. Please install it first.', 'Install Instructions', 'Open Terminal');
        if (action === 'Install Instructions') {
            vscode.env.openExternal(vscode.Uri.parse('https://github.com/gitgeistai/gitgeist-ai#installation'));
        }
        else if (action === 'Open Terminal') {
            const terminal = vscode.window.createTerminal('Gitgeist Install');
            terminal.sendText('pip install gitgeist');
            terminal.show();
        }
        throw new Error('Gitgeist not installed');
    }
}
function extractCommitMessage(output) {
    const patterns = [
        /Generated commit message:\s*(.+)/s,
        /💡.*Generated message:\s*(.+)/s,
        /Commit message:\s*(.+)/s
    ];
    for (const pattern of patterns) {
        const match = output.match(pattern);
        if (match) {
            return match[1].trim().replace(/^["']|["']$/g, '');
        }
    }
    return null;
}
async function showCommitDialog(commitMessage, cwd) {
    const action = await vscode.window.showInformationMessage(`🧠 Generated commit message:\n\n${commitMessage}`, { modal: true }, 'Commit', 'Copy to Clipboard', 'Edit Message');
    if (action === 'Commit') {
        try {
            await execAsync(`git commit -m "${commitMessage.replace(/"/g, '\\"')}"`, { cwd });
            vscode.window.showInformationMessage('✅ Commit created successfully!');
        }
        catch (error) {
            vscode.window.showErrorMessage(`Commit failed: ${error.message}`);
        }
    }
    else if (action === 'Copy to Clipboard') {
        await vscode.env.clipboard.writeText(commitMessage);
        vscode.window.showInformationMessage('📋 Commit message copied to clipboard!');
    }
    else if (action === 'Edit Message') {
        const editedMessage = await vscode.window.showInputBox({
            value: commitMessage,
            prompt: 'Edit the commit message',
            placeHolder: 'Enter your commit message'
        });
        if (editedMessage) {
            await showCommitDialog(editedMessage, cwd);
        }
    }
}
function handleError(error) {
    if (error.message.includes('gitgeist: command not found') || error.message.includes('Gitgeist not installed')) {
        return;
    }
    else if (error.message.includes('No configuration found')) {
        vscode.window.showErrorMessage('Gitgeist not initialized. Run "gitgeist init" in terminal first.', 'Open Terminal').then(action => {
            if (action === 'Open Terminal') {
                const terminal = vscode.window.createTerminal('Gitgeist Init');
                terminal.sendText('gitgeist init');
                terminal.show();
            }
        });
    }
    else {
        vscode.window.showErrorMessage(`Gitgeist error: ${error.message}`);
    }
}
function deactivate() { }
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map
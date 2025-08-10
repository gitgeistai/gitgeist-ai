# 📦 VS Code Extension Publishing Guide

## Prerequisites

1. **Visual Studio Marketplace Account**
   - Create account at: https://marketplace.visualstudio.com/manage
   - Create a publisher ID (e.g., "gitgeistai")

2. **Personal Access Token**
   - Go to: https://dev.azure.com/[your-org]/_usersSettings/tokens
   - Create token with "Marketplace (manage)" scope
   - Save the token securely

## Publishing Steps

### 1. Install VSCE (if not already installed)
```bash
npm install -g @vscode/vsce
```

### 2. Login to Marketplace
```bash
vsce login gitgeistai
# Enter your Personal Access Token when prompted
```

### 3. Publish Extension
```bash
# From extensions/vscode directory
vsce publish
```

### 4. Alternative: Manual Upload
If automatic publishing fails:
1. Package: `vsce package` (already done - creates .vsix file)
2. Go to: https://marketplace.visualstudio.com/manage
3. Upload the `gitgeist-vscode-0.3.0.vsix` file manually

## Pre-Publishing Checklist

- [x] Package.json metadata complete
- [x] README.md comprehensive
- [x] CHANGELOG.md updated
- [x] LICENSE file included
- [x] Extension compiles without errors
- [x] Extension packaged successfully
- [ ] Publisher account created
- [ ] Personal Access Token obtained
- [ ] Extension tested locally

## Testing Locally

Before publishing, test the extension:

```bash
# Install locally
code --install-extension gitgeist-vscode-0.3.0.vsix

# Or press F5 in VS Code to launch Extension Development Host
```

## Post-Publishing

1. **Verify Listing**: Check https://marketplace.visualstudio.com/items?itemName=gitgeistai.gitgeist-vscode
2. **Update Documentation**: Add marketplace link to main README
3. **Announce**: Share on social media, GitHub discussions
4. **Monitor**: Watch for user feedback and issues

## Marketplace Optimization

### Keywords for Discovery
- git, commit, ai, llm, ollama, semantic, automation, local, privacy

### Categories
- SCM Providers, Machine Learning, Other

### Description
"AI-powered Git commit generation using local LLMs. Generate intelligent commit messages with semantic code analysis."

## Version Management

For future updates:
1. Update version in `package.json`
2. Update `CHANGELOG.md`
3. Recompile and package
4. Publish with `vsce publish`

## Troubleshooting

**"Publisher not found"**
- Ensure publisher ID matches in package.json
- Create publisher at marketplace.visualstudio.com

**"Token expired"**
- Generate new Personal Access Token
- Login again with `vsce login`

**"Package too large"**
- Add `.vscodeignore` file to exclude unnecessary files
- Consider bundling with webpack

## Success Metrics

Track these after publishing:
- Downloads/installs
- User ratings and reviews
- GitHub issues and discussions
- Feature requests

---

**Ready to publish!** 🚀

The extension is packaged and ready for the VS Code Marketplace. Just need to create the publisher account and obtain the access token.
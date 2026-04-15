#!/bin/bash
# Forest GitHub Deployment Script
# Automates pushing Forest to GitHub

set -e

echo "🌲 Forest GitHub Deployment Script"
echo "===================================="
echo ""

# Check git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Install it first."
    exit 1
fi

# Get GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ Username required"
    exit 1
fi

# Verify we're in Forest directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Not in Forest directory. Run from /Users/llm01/Forest"
    exit 1
fi

REPO_URL="https://github.com/$GITHUB_USERNAME/forest.git"

echo "📦 Deployment Configuration"
echo "  Repository: $REPO_URL"
echo "  Branch: main"
echo "  Commits: $(git rev-list --count HEAD)"
echo ""

# Step 1: Check for secrets
echo "[1/5] 🔐 Scanning for secrets..."
SECRET_COUNT=$(git log -p 2>/dev/null | grep -i "password\|api_key\|secret\|token" | wc -l || true)

if [ "$SECRET_COUNT" -gt 0 ]; then
    echo "⚠️  Found $SECRET_COUNT potential secrets in commit history"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborting"
        exit 1
    fi
else
    echo "✅ No secrets detected"
fi
echo ""

# Step 2: Verify .gitignore
echo "[2/5] 📝 Verifying .gitignore..."
if [ -f ".gitignore" ]; then
    IGNORED_FILES=$(git ls-files --others --ignored --exclude-standard | wc -l)
    echo "✅ .gitignore found ($IGNORED_FILES files ignored)"
else
    echo "⚠️  No .gitignore found"
fi
echo ""

# Step 3: Check git status
echo "[3/5] ✅ Git status check..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Uncommitted changes found:"
    git status --short | head -10
    read -p "Commit and push anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborting"
        exit 1
    fi
fi
echo "✅ Working directory clean"
echo ""

# Step 4: Configure remote
echo "[4/5] 🔗 Configuring GitHub remote..."

# Remove existing remote if present
git remote remove origin 2>/dev/null || true

# Add new remote
git remote add origin "$REPO_URL"
git config --global credential.helper store

echo "✅ Remote configured: $(git remote get-url origin)"
echo ""

# Step 5: Push to GitHub
echo "[5/5] 🚀 Pushing to GitHub..."
echo ""

echo "Command: git push -u origin main"
echo ""
read -p "Ready to push? (Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "❌ Push cancelled"
    exit 1
fi

# Attempt push
echo "Pushing main branch..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Push successful!"
    echo ""
    echo "📊 Repository Stats"
    echo "  URL: $REPO_URL"
    echo "  Commits: $(git rev-list --count origin/main 2>/dev/null || echo "?")"
    echo "  Branches: $(git branch -a | wc -l)"
    echo ""
    echo "🎉 Forest is now live on GitHub!"
    echo ""
    echo "Next steps:"
    echo "  1. Go to $REPO_URL"
    echo "  2. Add repository topics: ai-agents, langgraph, kubernetes, docker"
    echo "  3. Enable GitHub Pages (optional)"
    echo "  4. Add GitHub Actions secrets if needed"
    echo ""
    echo "View on GitHub: $(echo $REPO_URL | sed 's/.git$//')"
else
    echo "❌ Push failed. Check credentials and try again."
    exit 1
fi

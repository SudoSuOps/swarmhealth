#!/bin/bash
# =============================================================================
# STINGER V2 — Git Setup Script
# stinger.swarmbee.eth
#
# Run this to initialize git and push to GitHub
# =============================================================================

set -e

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    STINGER V2 — GIT SETUP                            ║"
echo "║                    stinger.swarmbee.eth                              ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Initialize git if not already
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi

# Configure git (if not configured)
if [ -z "$(git config user.email)" ]; then
    echo ""
    echo "⚠️  Git user not configured. Setting defaults..."
    git config user.email "dev@trustcat.ai"
    git config user.name "TrustCat"
fi

# Add all files
echo ""
echo "📁 Adding files..."
git add -A

# Show status
echo ""
echo "📊 Git status:"
git status --short

# Create initial commit
echo ""
echo "💾 Creating initial commit..."
git commit -m "🎉 Stinger V2.0.0 — Diamond Hands Edition

Initial release of the intelligent medical AI gateway.

Features:
- Full end-to-end pipeline: Client → Stinger → QueenBee → Bumble70B → PDF
- DICOM, ECG, CGM parsers
- 15 gold clinical prompts
- Meditron-70B integration
- PDF report generation
- Merkle proofs + EIP-191 signing + IPFS
- SwarmPool job ledger
- ENS identity integration

Infrastructure:
- Tested on 2x RTX 5090
- Air-gap ready
- HIPAA-friendly

stinger.swarmbee.eth | trustcat.ai

💎 No shortcuts. No jeets. Diamond hands. 💎"

echo "✅ Commit created"

# Instructions for GitHub
echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    PUSH TO GITHUB                                    ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "To push to GitHub, run these commands:"
echo ""
echo "  # Add the remote (first time only)"
echo "  git remote add origin git@github.com:swarmhealth/stinger-v2.git"
echo ""
echo "  # Push to main branch"
echo "  git branch -M main"
echo "  git push -u origin main"
echo ""
echo "  # Or if using HTTPS:"
echo "  git remote add origin https://github.com/swarmhealth/stinger-v2.git"
echo "  git branch -M main"  
echo "  git push -u origin main"
echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    CREATE RELEASE                                    ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "After pushing, create a release:"
echo ""
echo "  # Create and push tag"
echo "  git tag -a v2.0.0 -m 'Stinger V2.0.0 — Diamond Hands Edition'"
echo "  git push origin v2.0.0"
echo ""
echo "  # Then go to GitHub and create a release from the tag"
echo ""
echo "💎 DIAMOND HANDS VERIFIED 💎"

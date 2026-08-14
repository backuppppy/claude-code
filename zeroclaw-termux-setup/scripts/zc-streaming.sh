#!/bin/bash
# ZeroClaw Streaming Mode Guide
# Streaming mode shows real-time output without waiting for approval

cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║           ZeroClaw Streaming Mode — Real-Time Output           ║
╚════════════════════════════════════════════════════════════════╝

🎯 What is Streaming Mode?
  Streaming mode outputs results in real-time without approval prompts.
  Perfect for quick commands and testing.

📝 Usage:

  1. Basic streaming command:
     echo "Y" | zeroclaw agent -a agggeeeenttt -m "הרץ ls -la" --stream

  2. Using alias (if configured):
     zcstream "הרץ pwd"

  3. Multiple commands:
     echo "Y" | zeroclaw agent -a agggeeeenttt -m "הרץ: git status && ls" --stream

🔄 How it works:
  - Sends "Y" to auto-approve all actions
  - Displays output as it comes
  - No waiting for confirmation prompts

⚙️ Configuration:
  - Risk profile: permissive (already configured)
  - No approval required
  - Full filesystem access

🛡️ Safety:
  - Still uses ZeroClaw's security constraints
  - Commands logged (no deletion of logs)
  - Can be reverted in config.toml if needed

📌 Examples:

  # Check git status
  zcstream "בדוק git status"

  # Run Python script
  zcstream "הרץ python3 script.py"

  # List files in directory
  zcstream "הרץ ls -la /path/to/dir"

  # Create and run script
  echo "Y" | zeroclaw agent -a agggeeeenttt \
    -m "כתוב ל-test.sh: #!/bin/bash && echo hello" --stream

═══════════════════════════════════════════════════════════════════

💡 Tip: Streaming mode is ideal for:
  ✓ Quick testing
  ✓ Development/iteration
  ✓ Real-time feedback
  ✓ Learning how ZeroClaw works

EOF

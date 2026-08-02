#!/bin/bash
# ZeroClaw Chat Loop — Interactive streaming mode
export HOME=/data/data/com.termux/files/home
export PATH=$HOME/.cargo/bin:$PATH

echo "🤖 ZeroClaw Chat (Streaming + YOLO Mode)"
echo "Type messages in Hebrew/English. Type 'quit' or 'exit' to stop."
echo "---"

while true; do
  read -p "you> " user_msg
  
  # Exit on quit/exit
  if [[ "$user_msg" =~ ^(quit|exit|bye|סוף)$ ]]; then
    echo "👋 Goodbye!"
    break
  fi
  
  # Skip empty input
  [[ -z "$user_msg" ]] && continue
  
  # Send to ZeroClaw with streaming
  echo ""
  zeroclaw agent -a agggeeeenttt -m "$user_msg" -v 2>&1 | grep -v '^\[system\]' | tail -100
  echo ""
done

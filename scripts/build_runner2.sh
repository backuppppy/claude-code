#!/bin/bash
WGET_PID=7550
NDK_ZIP=/root/.buildozer/android/platform/android-ndk-r25b-linux.zip
NDK_DIR=/root/.buildozer/android/platform/android-ndk-r25b
LOG=/tmp/buildozer6.log
APK_DIR=/storage/emulated/0/Download/tg_apk/bin

echo "$(date) ⏳ ממתין ל-wget PID $WGET_PID..."

while kill -0 $WGET_PID 2>/dev/null; do
  size=$(ls -lh "$NDK_ZIP" 2>/dev/null | awk '{print $5}')
  echo "$(date) 📥 NDK: $size"
  sleep 60
done

echo "$(date) ✅ wget סיים"

# בדוק גודל
ndk_size=$(stat -c%s "$NDK_ZIP" 2>/dev/null || echo 0)
echo "$(date) גודל ZIP: $ndk_size bytes"
if [ "$ndk_size" -lt 500000000 ]; then
  echo "$(date) ❌ NDK חסר ($ndk_size bytes) — הורדה נכשלה"
  exit 1
fi

# חלץ NDK אם לא קיים
if [ ! -d "$NDK_DIR" ]; then
  echo "$(date) 📦 מחלץ NDK..."
  cd /root/.buildozer/android/platform
  unzip -q "$NDK_ZIP"
  echo "$(date) ✅ NDK חולץ ל: $NDK_DIR"
else
  echo "$(date) ✅ NDK כבר קיים"
fi

# הרץ buildozer
echo "$(date) 🔨 מתחיל buildozer..."
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
export PATH="$JAVA_HOME/bin:/root/benv/bin:$PATH"
export VIRTUAL_ENV=/root/benv
export PIP_BREAK_SYSTEM_PACKAGES=1
export SETUPTOOLS_USE_DISTUTILS=local

cd /storage/emulated/0/Download/tg_apk
/root/benv/bin/buildozer android debug 2>&1 | tee "$LOG"

# תוצאה
if ls "$APK_DIR"/*.apk 2>/dev/null | grep -q apk; then
  echo "$(date) 🎉 APK מוכן: $(ls -lh $APK_DIR/*.apk)"
else
  echo "$(date) ❌ buildozer נכשל — בדוק $LOG"
fi

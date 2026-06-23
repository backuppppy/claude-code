#!/bin/bash
# ממתין ל-wget → מפעיל buildozer → מדווח תוצאה

WGET_PID=4731
LOG=/tmp/buildozer5.log
NDK=/root/.buildozer/android/platform/android-ndk-r25b-linux.zip
APK_DIR=/storage/emulated/0/Download/tg_apk/bin

echo "⏳ ממתין לסיום הורדת NDK (wget PID $WGET_PID)..."

# מעקב אחר wget עם דיווח התקדמות
while kill -0 $WGET_PID 2>/dev/null; do
  size=$(ls -lh "$NDK" 2>/dev/null | awk '{print $5}')
  echo "📥 NDK: $size מתוך ~516MB"
  sleep 60
done

# בדיקת קובץ NDK
ndk_size=$(stat -c%s "$NDK" 2>/dev/null || echo 0)
if [ "$ndk_size" -lt 500000000 ]; then
  echo "❌ NDK הורד חלקית ($ndk_size bytes) — בעיה בהורדה"
  exit 1
fi

echo "✅ NDK הורד בהצלחה ($(ls -lh $NDK | awk '{print $5}'))"
echo "🔨 מתחיל buildozer..."

export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
export PATH="$JAVA_HOME/bin:/root/benv/bin:$PATH"
export VIRTUAL_ENV=/root/benv
export PIP_BREAK_SYSTEM_PACKAGES=1
export SETUPTOOLS_USE_DISTUTILS=local

cd /storage/emulated/0/Download/tg_apk
/root/benv/bin/buildozer android debug 2>&1 | tee "$LOG"

# בדיקת תוצאה
if ls "$APK_DIR"/*.apk 2>/dev/null | grep -q apk; then
  echo "🎉 APK מוכן: $(ls -lh $APK_DIR/*.apk)"
else
  echo "❌ buildozer נכשל. בדוק $LOG לפרטים"
fi

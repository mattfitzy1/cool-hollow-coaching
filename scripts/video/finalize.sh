#!/bin/bash
# Mux the silent animation with the voice+music soundtrack into the final MP4.
set -e
cd /Users/matthewfitzpatrick-buck/Desktop/matthew-fitzpatrick-aios-main
DIR=outputs/videos/cool-hollow-brand
ffmpeg -y -i "$DIR/silent.mp4" -i "$DIR/master.wav" \
  -c:v copy -c:a aac -b:a 192k -shortest \
  "$DIR/cool-hollow-brand-explainer.mp4"
echo "FINAL: $DIR/cool-hollow-brand-explainer.mp4"
ls -lh "$DIR/cool-hollow-brand-explainer.mp4" | awk '{print $5}'

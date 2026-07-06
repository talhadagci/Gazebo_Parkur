#!/bin/bash
# Teknofest parkurunu Gazebo'da acar. Kullanim: ./baslat.sh
set -e

REPO_DIZINI="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_BUILD="$REPO_DIZINI/parkur/plugins/kayar_engel/build"

# Kayar engel plugin'i derlenmemisse derle
if [ ! -f "$PLUGIN_BUILD/libkayar_engel_plugin.so" ]; then
    echo ">> Kayar engel plugin'i derleniyor..."
    mkdir -p "$PLUGIN_BUILD"
    cd "$PLUGIN_BUILD"
    cmake .. -DCMAKE_BUILD_TYPE=Release
    make -j"$(nproc)"
    cd - > /dev/null
fi

# model://parkur/... URI'lerinin cozulmesi icin repo koku model yolu olmali
export GAZEBO_MODEL_PATH="$REPO_DIZINI:$GAZEBO_MODEL_PATH"
export GAZEBO_PLUGIN_PATH="$PLUGIN_BUILD:$GAZEBO_PLUGIN_PATH"
# Online model veritabaninda takilmayi onle
export GAZEBO_MODEL_DATABASE_URI=""

exec gazebo "$REPO_DIZINI/parkur/worlds/parkur_yeni.world" "$@"

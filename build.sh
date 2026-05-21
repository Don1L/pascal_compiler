#!/bin/bash
# build.sh — сборка и запуск Pascal-компилятора через Docker
#
# Использование:
#   ./build.sh build                          — собрать Docker-образ
#   ./build.sh vm   examples/factorial.pas    — запустить через VM
#   ./build.sh x86  examples/factorial.pas    — сгенерировать .asm и запустить
#   ./build.sh asm  examples/factorial.pas    — только показать .asm листинг
#   ./build.sh dis  examples/factorial.pas    — показать байткод VM

IMAGE="pascal-compiler"
SRC_DIR="$(pwd)"

case "$1" in

  build)
    echo "Сборка Docker-образа..."
    docker build -t $IMAGE .
    ;;

  vm)
    FILE="${2:-examples/hello.pas}"
    docker run --rm -v "$SRC_DIR":/pascal $IMAGE "$FILE" --vm
    ;;

  x86)
    FILE="${2:-examples/hello.pas}"
    BASE=$(basename "$FILE" .pas)
    ASM_FILE="examples/${BASE}.asm"
    OBJ_FILE="/tmp/${BASE}.o"
    BIN_FILE="/tmp/${BASE}"

    echo "Генерируем листинг..."
    docker run --rm -v "$SRC_DIR":/pascal $IMAGE "$FILE" --x86 --out "$ASM_FILE"

    echo "Собираем через NASM..."
    docker run --rm -v "$SRC_DIR":/pascal --entrypoint bash $IMAGE -c "
      nasm -f elf32 /pascal/$ASM_FILE -o $OBJ_FILE &&
      gcc -m32 -no-pie $OBJ_FILE -o $BIN_FILE &&
      echo '--- Результат ---' &&
      $BIN_FILE
    "
    ;;

  asm)
    FILE="${2:-examples/hello.pas}"
    docker run --rm -v "$SRC_DIR":/pascal $IMAGE "$FILE" --x86
    ;;

  dis)
    FILE="${2:-examples/hello.pas}"
    docker run --rm -v "$SRC_DIR":/pascal $IMAGE "$FILE" --vm --dis
    ;;

  *)
    echo "Использование:"
    echo "  ./build.sh build                        — собрать образ"
    echo "  ./build.sh vm   examples/factorial.pas  — запустить через VM"
    echo "  ./build.sh x86  examples/factorial.pas  — собрать и запустить x86"
    echo "  ./build.sh asm  examples/factorial.pas  — показать .asm листинг"
    echo "  ./build.sh dis  examples/factorial.pas  — показать байткод VM"
    ;;

esac

#!/bin/sh

if [ $# -eq 0 ]; then
  mkdir -p /usr/local/bin
  cp -f imagem.py /usr/local/bin/imagem
  chmod 755 /usr/local/bin/imagem
  mkdir -p /usr/local/share/man/man1
  cp -f imagem.1 /usr/local/share/man/man1
  chmod 644 /usr/local/share/man/man1/imagem.1
else
  if [[ "$1" != "uninstall" ]]; then
    echo "Invalid argument: $1"
    exit 1
  fi
  rm /usr/local/bin/imagem
  rm /usr/local/share/man/man1/imagem.1
fi

#!/bin/sh
# 컨테이너 공통 진입점.
# · 마이그레이션은 여기서 실행하지 않는다 — 배포 절차 3단계에서 별도로 돌린다(§12.2).
# · DB 가 뜰 때까지 짧게 기다린 뒤 넘겨준다.
set -e

if [ "${WAIT_FOR_DB:-1}" = "1" ]; then
  i=0
  until python -c "import socket,os,sys; s=socket.create_connection((os.environ.get('POSTGRES_HOST','db'), int(os.environ.get('POSTGRES_PORT','5432'))), 2)" 2>/dev/null; do
    i=$((i+1))
    if [ "$i" -gt 60 ]; then
      echo "DB 연결 대기 시간 초과" >&2
      exit 1
    fi
    sleep 1
  done
fi

exec "$@"

#!/bin/sh
# NDG のjob実行シェル.

# 実行時の日付を取得する.
arg=$(date "+%Y%m%d%H%M")

# 実行基日を取得する。
conddate=$(date "+%Y%m%d")
# 実行開始ログを出力する。
. /Users/masuyamakouta/scraping/bin/activate

while true ; do
# 実行時の日付を取得する.
arg=$(date "+%Y%m%d%H%M")
argday=$(date "+%Y%m%d")
# pythonの実行
python ${APPMONEYTRADE}batch/getData/NDGNowDataGet.py ${arg}
python ${APPMONEYTRADE}batch/getpairData/PNGPairNowGet.py ${arg}
sleep 5
done

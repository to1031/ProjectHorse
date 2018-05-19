#!/bin/sh
# 作成日 2018/04/10
# 作成者
# 機能名：システムトレード
# STRE.sh


# 1.前処理
# 1.1 仮想環境のディレクトリ取得
ENVDIR=${HOME}'/scraping'

# 1.2 仮想環境の起動
. ${ENVDIR}/bin/activate

# 1.3 実行時の日付を取得する.
arg=$(date "+%Y%m%d%H%M")

# 1.4 実行基日を取得する。
conddate=$(date "+%Y%m%d")

# 2.プログラムyobidashi
while true ; do
# 実行時の日付を取得する.
arg=$(date "+%Y%m%d%H%M")
argday=$(date "+%Y%m%d")
# pythonの実行
python ${APPMONEYTRADE}batch/systetrade/STRESystemTradeExe.py ${arg}
sleep 2
done

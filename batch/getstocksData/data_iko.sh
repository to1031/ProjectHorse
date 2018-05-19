#!/bin/sh

# NDG のjob実行シェル.
# 実行開始ログを出力する。
. /Users/masuyamakouta/ProjectHorse/bin/activate

ARRAYY=(2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015 2017 2018)
ARRAYM=(01 02 03 04 05 06 07 08 09 10 11 12)
ARRAYD=(01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31)
for year in ${ARRAYY[@]}
do
for month in ${ARRAYM[@]} 
do
for day in ${ARRAYD[@]} 
do
python /Users/masuyamakouta/ProjectHorse/project/ProjectMoneyTrade/source/getstocksData/STGStocksTodayGet.py ${year}${month}${day}
done
done
done

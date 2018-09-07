#!/usr/bin/env bash

root=$(cd "$(dirname "$0")"; cd ../..; pwd)
protodir=$root/bin/thrift/security
svnbase=svn://10.1.2.128/formax_trunk/formax_social/protocols/
gendir=$root/thrifts/security

# 需要拉取的协议文件
files=(security)

# 删除之前的 thrift 文件和代码
rm -rf $protodir $gendir

if [ ! -d $protodir ]; then
    mkdir -p $protodir
fi

if [ ! -d $gendir ]; then
    mkdir -p $gendir
fi

for file in ${files[@]}; do
    svn cat $svnbase/$file.thrift > $protodir/$file.thrift
    sed -i '/^namespace\s*py/d' $protodir/$file.thrift # 移除命名空间
done

# 重新生成 php 代码
for file in $protodir/*.thrift; do
    thrift -v -r --out $gendir --gen py $file
done

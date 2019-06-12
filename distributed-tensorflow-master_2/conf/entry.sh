#!/bin/bash

if [ $# != 9 ]
then
    echo "ERROR: args number not equal 9"
    exit 1
fi

NAME=$1
INDEX=$2
PS_HOSTS=$3
WORKER_HOSTS=$4
CODE_PACKAGE=$5
DATA=$6
EXPORT=$7
HDFS_URL=$8
HDFS_NN=$9


DOWNLOAD_URL="$HDFS_URL/webhdfs/v1$CODE_PACKAGE?op=open&user.name=root"
echo "====== start download code from $DOWNLOAD_URL ======"
wget --timeout=20 --tries=1 $DOWNLOAD_URL -O train_code.tgz
if [ $? -ne 0 ]; then
    echo "download $DOWNLOAD_URL failed, exit 2"
    exit 2
fi

mkdir /notebooks/train_code && tar -zxf train_code.tgz -C /notebooks/train_code && source /etc/profile

python /notebooks/train_code/start.py --job_name=$NAME --task_index=$INDEX --ps_hosts=$PS_HOSTS --worker_hosts=$WORKER_HOSTS

if [ $? -ne 0 ]
then
    echo "execute code failed"
    exit 4
fi

# test only
#sleep 3600

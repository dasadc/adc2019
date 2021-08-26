#! /bin/bash
#
#
# 出題された問題データを、チェックする


echo "get-q"

# Create working directory
work_dir="tmp".$$
mkdir ${work_dir} || exit 1
echo working directory: ${work_dir}
cd ${work_dir}

# Download all Q file
n=1
adccli get-q | while read line
do
    echo $n: $line
    qnum=$(echo $line | sed -n 's:^Q\([0-9]*\).*:\1:p')
    adccli --output Q${qnum}.txt get-q ${qnum} || exit 1
    n=$((n + 1))
done

# Download all-in-one zip file and compare files
mkdir zip
cd zip
adccli --output Q.zip get-q-all
unzip Q.zip

for i in Q*.txt
do
    echo diff -u ../${i} ${i}
    diff -u ../${i} ${i} || exit 1
done

cd ../../
rm -r ${work_dir}
echo delete working directory: ${work_dir}

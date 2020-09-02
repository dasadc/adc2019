#!bash

#jsfile=$1
#jsfiledir="$(dirname "$(readlink -f "$0")")"

qfile=$1
afile=$2

#docker run --rm -v `pwd`:/work geekduck/node-canvas $jsfile /work/$qfile /work/$afile 2>/dev/null
#docker run --rm -v `pwd`:/opt/node/js geekduck/node-canvas $jsfile $qfile $afile
#docker run --rm -v ${jsfiledir}:/opt/node/js geekduck/node-canvas $jsfile $qfile $afile

#docker run --rm -v `pwd`:/work viewer/node-canvas viewer_node.js /work/$qfile /work/$afile
docker run --rm -v `pwd`:/work viewer/node-canvas viewer_node.js /work/$qfile /work/$afile 2>/dev/null
python ~/work/github/dasadc/adc2019/server/adc2019.py -Q $qfile -A $afile

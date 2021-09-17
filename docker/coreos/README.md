Fedora CoreOSのセットアップ
===========================

### SSH鍵の作成

``` bash
ssh-keygen -f ./id_rsa -C adc@das -N ""
```

### butaneを使ってignitionファイルを作成する

`example2.bu`を作成した。



``` bash
docker pull quay.io/coreos/butane:release

docker run --interactive --rm --security-opt label=disable --volume ${PWD}:/pwd --workdir /pwd quay.io/coreos/butane:release --strict example2.bu > example2.ign
```

出来上がった`example2.ign`を、httpdが動いているホストへコピーする。


### install CoreOS


``` bash
sudo coreos-installer install /dev/sda --ignition-url http://192.168.0.1/example2.ign --insecure-ignition
```



参考にしたドキュメント
---------------------

- https://docs.fedoraproject.org/en-US/fedora-coreos/producing-ign/
- https://docs.fedoraproject.org/en-US/fedora-coreos/kernel-args/#_example_staying_on_cgroups_v1

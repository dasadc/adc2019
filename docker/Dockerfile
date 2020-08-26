FROM	centos:8
ENV container docker
RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == \
systemd-tmpfiles-setup.service ] || rm -f $i; done); \
rm -f /lib/systemd/system/multi-user.target.wants/*;\
rm -f /etc/systemd/system/*.wants/*;\
rm -f /lib/systemd/system/local-fs.target.wants/*; \
rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
rm -f /lib/systemd/system/basic.target.wants/*;\
rm -f /lib/systemd/system/anaconda.target.wants/*;
VOLUME [ "/sys/fs/cgroup" ]
CMD ["/usr/sbin/init"]

ADD	opt_miniconda3.tar.gz /
COPY	google-cloud-sdk.repo /etc/yum.repos.d/
COPY	dot_bashrc /home/adc/.bashrc
WORKDIR	/home/adc
RUN	yum clean all && \
	yum update -y && \
	yum install -y \
	    bash-completion \
	    epel-release \
	    gcc-c++ \
	    git \
	    less \
	    make \
	    openssh-server \
	    rsync \
	    sudo \
	    which \
	    google-cloud-sdk \
	    google-cloud-sdk-datastore-emulator \
	    google-cloud-sdk-app-engine-python && \
	yum clean all && \
	systemctl enable sshd && \
	systemctl enable systemd-user-sessions && \
	ln -s ../systemd-user-sessions.service /usr/lib/systemd/system/multi-user.target.wants/systemd-user-sessions.service ; \
	groupadd -g 1000 adc && \
	useradd -m -s /bin/bash -g adc -u 1000 -p '$6$ipsjdasadc$j3jCv7RIO3CDs4dBWBsRHvLAjQe3tln.TdQdRVcBTM6fa3FL7.jz7hkCRxtoQxq4eX64twQRwqdvtqHBaQDmR/' adc && \
	usermod -a -G wheel adc && \
	cd /home/adc/ && \
	git clone -b adc2020-yt --single-branch https://github.com/dasadc/adc2019.git && \
	chown -R 1000:1000 /home/adc/ && \
	cp /home/adc/adc2019/server/adc-datastore.service /etc/systemd/system/ && \
	systemctl enable adc-datastore && \
	cp /home/adc/adc2019/server/adc-apiserver.service /etc/systemd/system/ && \
	systemctl enable adc-apiserver

USER	adc

RUN	source /opt/miniconda3/bin/activate py38 && \
	cd /home/adc/adc2019/client-app/ && \
	npm install && \
	gcloud config set project test813

COPY	dot_bash_profile /home/adc/.bash_profile
COPY	dot_bash_logout  /home/adc/.bash_logout

USER	root

EXPOSE	80 4200 4280 8000 8080 8888 18000 28000

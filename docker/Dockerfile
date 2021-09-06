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

COPY    Miniforge3-Linux-x86_64.sh /tmp/
COPY	google-cloud-sdk.repo /etc/yum.repos.d/

ENV CLOUDSDK_PYTHON=python3
ENV CLOUDSDK_GSUTIL_PYTHON=python3
ENV CLOUDSDK_BQ_PYTHON=python3

RUN     groupadd -g 1000 adc && \
	useradd -m -s /bin/bash -g adc -u 1000 -p '$6$ipsjdasadc$j3jCv7RIO3CDs4dBWBsRHvLAjQe3tln.TdQdRVcBTM6fa3FL7.jz7hkCRxtoQxq4eX64twQRwqdvtqHBaQDmR/' adc && \
	usermod -a -G wheel adc && \
	mkdir /opt/miniforge3 && \
	chown adc:adc /opt/miniforge3 && \
	yum clean all && \
	yum update -y && \
	yum install -y \
	    bash-completion \
	    git \
	    less \
	    openssh-server \
	    rsync \
	    sudo \
	    which \
	    python39

RUN	yum install -y \
	    google-cloud-sdk \
	    google-cloud-sdk-datastore-emulator \
	    google-cloud-sdk-app-engine-python && \
	yum clean all


RUN	systemctl enable sshd

#	systemctl enable systemd-user-sessions
#	ln -s ../systemd-user-sessions.service /usr/lib/systemd/system/multi-user.target.wants/systemd-user-sessions.service

USER    adc
WORKDIR	/home/adc
COPY	dot_bashrc            /home/adc/.bashrc
COPY	dot_bash_profile      /home/adc/.bash_profile
COPY	dot_bash_logout       /home/adc/.bash_logout
RUN	/bin/sh /tmp/Miniforge3-Linux-x86_64.sh -b -p /opt/miniforge3 -u && \
	rm /tmp/Miniforge3-Linux-x86_64.sh && \
	/opt/miniforge3/bin/conda update --yes -n base -c defaults conda && \
	/opt/miniforge3/bin/conda config --set auto_activate_base false && \
	cd /home/adc/ && \
	git clone -b adc2021-yt --single-branch https://github.com/dasadc/adc2019.git && \
	gcloud config set project das-adc
RUN	/opt/miniforge3/bin/conda create -n adc2019dev python=3.9 flask=1.1.2 flask-cors=3.0.10 numpy gunicorn grpcio pytz requests protobuf pyyaml nodejs=14 google-cloud-datastore pandas openpyxl

USER    root
RUN	cp /home/adc/adc2019/server/adc-datastore.service /etc/systemd/system/ && \
	systemctl enable adc-datastore && \
	cp /home/adc/adc2019/server/adc-server.service /etc/systemd/system/ && \
	systemctl enable adc-server

EXPOSE	22 80 4200 4280 8000 8080 8888 18000 28000

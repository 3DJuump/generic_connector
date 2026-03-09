FROM docker.io/debian:trixie-slim

# deploy deb packages
COPY docker/tmp/*.deb /tmp/

# set package install non interactive
ARG DEBIAN_FRONTEND=noninteractive

# update apt
RUN apt update
RUN apt --assume-yes upgrade

# configure locale
RUN install_packages locales
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
RUN locale-gen
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
RUN export

# need adduser
RUN apt --assume-yes install adduser

# pre-install dependencies
COPY docker/tmp/install_deb_dependencies.sh /tmp/install_deb_dependencies.sh
RUN /bin/bash /tmp/install_deb_dependencies.sh

# create juumpinfinite user
RUN adduser juumpinfinite
RUN passwd -d juumpinfinite

# accept eula
RUN echo "lib3djuump-infinite-cli lib3djuump-infinite-cli/eula string yes" > /tmp/debconf.conf
RUN debconf-set-selections /tmp/debconf.conf

# install deb packages
RUN dpkg --force-all -i /tmp/*.deb

# remove tmp files deb packages
RUN rm -rf /tmp/*

# install usefull tools
RUN install_packages curl python3 python3-requests python3-yaml python3-psutil python3-jsonschema vim htop

# copy connector files
COPY ../converter3dji.py ../generic_connector.py ../connector_conf.schema.json /generic_connector/
COPY ../prj_tpl/project_conf.json.tpl ../prj_tpl/project_conf.schema.json /generic_connector/prj_tpl/
COPY ../prj_tpl/project_custo.py /generic_connector/prj_tpl/
COPY ../prj_tpl/docs/* /generic_connector/prj_tpl/docs/
COPY ./docker/meta_connector.py ./docker/README.md /generic_connector/

COPY ./docker/init.py /init.py
COPY ./docker/entrypoint.sh /entrypoint.sh
RUN ["chmod","+x","/entrypoint.sh"]
RUN ["chmod","+x","/generic_connector/generic_connector.py"]
RUN ["chmod","+x","/generic_connector/meta_connector.py"]
RUN ["chmod","-R","+r","/generic_connector"]
RUN ["chown","-R","juumpinfinite","/generic_connector"]

WORKDIR /connector
RUN ["chown","juumpinfinite","/connector"]

USER juumpinfinite
RUN ["mkdir","-p","/home/juumpinfinite/.3djuump-infinite-cli"]
RUN ["ln","-s","/connector/_scripts/conf_4_1.json","/home/juumpinfinite/.3djuump-infinite-cli/conf_4_1.json"]
ENV CONNECTOR_MODE=sleep
ENTRYPOINT [ "/entrypoint.sh" ]
#ENTRYPOINT ["sleep", "500000000000000000000000000000000000000"]
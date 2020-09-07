FROM ubuntu:18.04

# System packages 
RUN apt-get update && apt-get install -y curl

# Install miniconda to /miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda
RUN apt-get install redis-server -y
RUN apt-get install git -y
RUN apt-get install openjdk-8-jdk -y
RUN apt-get install maven -y
RUN apt-get install bash -y 
RUN apt-get install p7zip-full -y
RUN apt-get install build-essential -y
RUN apt-get install automake -y
RUN apt-get install autoconf -y
RUN apt-get install opam -y
RUN opam init -y
RUN eval `opam config env`
RUN opam install ocamlfind -y
RUN opam install ocamlbuild -y

WORKDIR /data/
RUN git clone https://gitlab.inria.fr/spinfer/spinfer
RUN cd spinfer && git submodule update --init

RUN eval `opam config env` && cd spinfer && bash build_dependencies.sh

RUN cd spinfer && rm coccinelle/tools/spgen/source/spgen_lexer.ml
RUN eval `opam config env` && cd spinfer && make build



RUN apt-get update && apt-get install --no-install-recommends -y \
    curl \
    zip \
    g++ \
    make \
    ninja-build \
    antlr \
    libantlr-dev \
    libxml2-dev \
    libxml2-utils \
    libxslt1-dev \
    libarchive-dev \
    libssl-dev \
    libcurl4-openssl-dev \
    cpio \
    man \
    file \
    dpkg-dev \
    && rm -rf /var/lib/apt/lists/*

# Download and install a newer binary version of cmake
ARG CMAKE_BIN_URL=https://cmake.org/files/v3.14/cmake-3.14.1-Linux-x86_64.tar.gz
RUN curl -L $CMAKE_BIN_URL | tar xz --strip-components=1 -C /usr/local/

# Download and install only needed boost files
RUN curl -L http://www.sdml.cs.kent.edu/build/srcML-1.0.0-Boost.tar.gz | \
    tar xz -C /usr/local/include

# Allow man pages to be installed
RUN sed -i '/path-exclude=\/usr\/share\/man\/*/c\#path-exclude=\/usr\/share\/man\/*' /etc/dpkg/dpkg.cfg.d/excludes


RUN curl -LO http://131.123.42.38/lmcrs/v1.0.0/srcML-1.0.0.tar.gz
RUN tar xvf srcML-1.0.0.tar.gz
RUN cd srcML-1.0.0 && cmake .
RUN cd srcML-1.0.0 && make install 
RUN ldconfig

RUN git config --global user.name "flexi"
RUN git config --global user.email "flexi@flexi.com"
RUN git clone --single-branch --branch master https://github.com/FlexiRepair/FlexiRepair.git
#RUN mkdir flexi-data
RUN apt-get update && apt-get install nano -y
RUN conda env create -f flexi/environment.yml

RUN curl -LO http://www.comp.nus.edu.sg/~release/codeflaws/codeflaws.tar.gz
RUN tar xf codeflaws.tar.gz
WORKDIR /data/flexi/
RUN git pull && mvn clean install



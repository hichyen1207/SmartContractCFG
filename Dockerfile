FROM ubuntu:16.04

LABEL maintainer="Harrison <hichyen1207@gmail.com>"

RUN apt-get update
RUN apt-get install -y software-properties-common

RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update
RUN apt-get install -y python3.6 python3-pip python3.6-dev
RUN python3.6 -m pip install pip --upgrade

RUN add-apt-repository -y ppa:ethereum/ethereum
RUN add-apt-repository -y ppa:ethereum/ethereum-dev
RUN apt-get update
RUN apt-get install -y ethereum curl graphviz

RUN curl -o /usr/bin/solc -fL https://github.com/ethereum/solidity/releases/download/v0.4.25/solc-static-linux \
    && chmod u+x /usr/bin/solc

COPY ./requirements.txt /SmartContractCFG/requirements.txt
WORKDIR /SmartContractCFG/
RUN pip3 install -r requirements.txt
RUN pip3 install z3-solver
COPY . /SmartContractCFG/
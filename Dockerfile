FROM ubuntu:18.04

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y \
        curl \
        libc-dev \
        gcc \
        make \
        openjdk-11-jdk-headless \
        python3 \ 
        python3-pip \
 && rm -rf /var/lib/apt/lists/*



# Install dependencies
ADD Pipfile Pipfile

RUN pip3 install pipenv \
 && pipenv install --system --skip-lock

# Add files
ADD src/ src/

EXPOSE 8090

ENTRYPOINT [ "python", "src/__main__.py" ]
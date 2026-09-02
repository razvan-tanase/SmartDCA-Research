FROM debian:bookworm-20260824-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        latexmk \
        lmodern \
        poppler-utils \
        python3 \
        texlive-fonts-recommended \
        texlive-latex-base \
        texlive-latex-recommended \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work
ENTRYPOINT ["python3", "manuscript/build.py"]

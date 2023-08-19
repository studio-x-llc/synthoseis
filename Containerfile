FROM python:3.10

RUN mkdir -p /opt/synthoseis
COPY ./pyproject.toml ./poetry.lock ./README.md /opt/synthoseis
COPY ./synthoseis /opt/synthoseis/synthoseis
COPY ./config /opt/synthoseis/defaults

ENV PATH="/root/.local/bin:$PATH"

WORKDIR "/opt/synthoseis"

RUN pip install pipx \
    && pipx install poetry \
    && poetry install

ENTRYPOINT [ "poetry", "run", "python", "-m", "synthoseis.run" ]

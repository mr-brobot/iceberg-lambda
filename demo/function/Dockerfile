FROM public.ecr.aws/lambda/python:3.10 AS requirements

# poetry
ENV POETRY_NO_INTERACTION=yes \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.5.1 \
    POETRY_HOME="/opt/poetry"
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /lambda/src/

COPY poetry.lock pyproject.toml ./

RUN poetry export --output requirements.txt --without-hashes --without-urls

FROM public.ecr.aws/lambda/python:3.10

# git
RUN yum install -y git

COPY --from=requirements /lambda/src/requirements.txt .

RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY . ${LAMBDA_TASK_ROOT}
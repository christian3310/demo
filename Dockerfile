FROM public.ecr.aws/lambda/python:3.9

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ENV AWS_REGION=us-east-1

WORKDIR /srv
COPY . .

RUN pip install -U poetry
RUN poetry install --no-dev

ENTRYPOINT [ "poetry", "run" ]
CMD python -m app

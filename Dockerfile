FROM public.ecr.aws/lambda/python:3.9

ARG _AWS_ACCESS_KEY_ID
ARG _AWS_SECRET_ACCESS_KEY
ARG _AWS_REGION=us-east-1
ARG _BUCKET=stock-data-demo

ENV AWS_ACCESS_KEY_ID=${_AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${_AWS_SECRET_ACCESS_KEY}
ENV AWS_REGION=${_AWS_REGION}
ENV S3_BUCKET=${_BUCKET}

WORKDIR /srv
COPY . .

RUN pip install -U poetry
RUN poetry install --no-dev

ENTRYPOINT [ "poetry", "run" ]
CMD [ "python", "-m", "app", "-b", "${S3_BUCKET}" ]

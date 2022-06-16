FROM public.ecr.aws/lambda/python:3.9

WORKDIR /srv
COPY . .

RUN pip install -U poetry
RUN poetry install

ENTRYPOINT [ "poetry", "run" ]
CMD python -m app

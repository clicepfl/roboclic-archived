FROM python:alpine3.18

WORKDIR /app

RUN adduser --system nonroot
USER nonroot

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY robot/ ./robot
COPY roboclic.py ./

ENTRYPOINT [ "python", "roboclic.py" ]
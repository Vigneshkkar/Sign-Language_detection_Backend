FROM python:3.8-alpine

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

RUN /usr/local/bin/python -m pip install --upgrade pip
# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY . /app
ENV FLASK_APP app.py
ENV FLASK_ENV development

# configure the container to run in an executed manner
# ENTRYPOINT [ "python" ]

CMD ["flask", "run", "--host=0.0.0.0" ]
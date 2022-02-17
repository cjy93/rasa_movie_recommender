FROM rasa/rasa

ENV BOT_ENV=production

COPY . /var/www
WORKDIR /var/www

#RUN pip install rasa==3.0.8
# Install project dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip --user
RUN pip install --no-cache-dir -r requirements.txt --use-deprecated=legacy-resolver --user
RUN rasa train

ENTRYPOINT [ "rasa", "run", "-p", "8080"]

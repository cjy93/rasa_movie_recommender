FROM rasa/rasa

ENV BOT_ENV=production

COPY . /var/www
WORKDIR /var/www

#RUN pip install rasa==3.0.8
# Install project dependencies
COPY ./requirements.txt .
RUN /home/jiayi_ca2/miniconda3/envs/rasabot/bin/python3 -m pip install --upgrade pip
RUN /home/jiayi_ca2/miniconda3/envs/rasabot/bin/python3 -m pip install --no-cache-dir -r requirements.txt --use-deprecated=legacy-resolver
RUN rasa train

ENTRYPOINT [ "rasa", "run", "-p", "8080"]

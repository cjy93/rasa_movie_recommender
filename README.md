# rasa_movie_recommender
Movie recommender system with IMDB data and RASA python

This is for CA2 of AIHI
# To Run
Connect to the webhook from local to the facebook service with ngrok  

Open First command window type:
`python -m rasa run --credentials credentials.yml`

If you did not set up deployment to facebook, type:
`python -m rasa shell`

Open Second command window type:
`python -m rasa run actions`

If you want to retrain your model, type:
`python -m rasa train`

# Notes
1) Since my GCP detected I am using `Python` runtime, they asked me to remove Dockerfile. Instead, i need to install these separately by having a `requirements.txt` file
```
Flask==0.10.1
gunicorn==19.3.0
twilio==6.8.4
```

2) If you get entrypoint error such as no "main" file, follow this:
[entrypoint error](https://cloud.google.com/appengine/docs/standard/python3/runtime#application_startup)
## Enable API
[Enable API](https://cloud.google.com/source-repositories/docs/quickstart-triggering-builds-with-source-repositories#grant_gae_name_access_to_the_builder_name_service_account)
[deploying to App Engine](https://cloud.google.com/build/docs/deploying-builds/deploy-appengine#yaml_1)

# Important references:
Pay close attention to these references on how to set up deployment on GCP.

[set up GCP](https://cloud.google.com/resource-manager/docs/creating-managing-projects#creating_a_project)  
[follow how he set up the Dockerfile and app.yaml](https://github.com/hassaanseeker/Rasa-GCP)  
[follow this newest app.yaml config file!](https://cloud.google.com/appengine/docs/flexible/python/configuring-your-app-with-app-yaml)
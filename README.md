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
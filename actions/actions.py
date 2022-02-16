# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

# Default
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
from rasa_sdk.types import DomainDict

# for Movie IMDB
import pandas as pd
from gensim.models.doc2vec import Doc2Vec
from gensim.parsing.preprocessing import preprocess_string

# for converting string representation of list to real list
import ast

# Load ML model1
model = Doc2Vec.load("movies_doc2vec")  # use the full path
# Load dataset to get movie titles
df = pd.read_csv(
    "wiki_movie_plots_deduped.csv", sep=",", usecols=["Release Year", "Title", "Plot"]
)  # use the full path
df = df[df["Release Year"] >= 2000]


class ActionMovieTitle(Action):
    def name(self) -> Text:
        return "action_movie_title"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # Load dataframe top250
        df_top250 = pd.read_csv("top250.csv", sep=",")
        # do not truncate hyperlinks
        pd.set_option("display.max_colwidth", None)
        # take in the typed message
        userMessage = tracker.latest_message["text"]
        # use model to find the movie
        index = df_top250.index
        # use model to find the movie
        condition = index[df_top250["Title"].str.lower() == userMessage.lower()]
        index_list = condition.tolist()
        image_poster = df_top250["Poster"].loc[index_list[0]]
        print("image poster: ", image_poster)

        link = df_top250[df_top250["Title"].str.lower() == userMessage.lower()][
            "imdb_link"
        ]

        if len(link) > 0:
            botResponse = f"I found the following link and poster : {link}".replace(
                "[", ""
            ).replace("]", "")
        else:
            botResponse = f"Movie title is not in list, please find another title"
        dispatcher.utter_message(text=botResponse)
        dispatcher.utter_message(image=image_poster)
        return []


class ActionMovieSearch(Action):
    def name(self) -> Text:
        return "action_movie_search"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        userMessage = tracker.latest_message["text"]
        # use model to find the movie
        new_doc = preprocess_string(userMessage)
        test_doc_vector = model.infer_vector(new_doc)
        sims = model.dv.most_similar(positive=[test_doc_vector])
        # Get first 5 matches
        movies = [df["Title"].iloc[s[0]] for s in sims[:5]]

        botResponse = f"I found the following movies: {movies}.".replace(
            "[", ""
        ).replace("]", "")
        dispatcher.utter_message(text=botResponse)
        return []


class ValidateRestaurantForm(Action):
    def name(self) -> Text:
        return "user_details_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        required_slots = ["name", "number"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # the slot is not filled yet. Request the user to fill this slot next
                return [SlotSet("requested_slot", slot_name)]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]


class ValidateMovieForm(Action):
    def name(self) -> Text:
        return "user_movie_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        required_slots = ["genre", "year", "language"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # the slot is not filled yet. Request the user to fill this slot next
                return [SlotSet("requested_slot", slot_name)]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]


class ActionSubmit(Action):
    def name(self) -> Text:
        return "action_submit"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            template="utter_details_thanks",
            Name=tracker.get_slot("name"),
            Mobile_number=tracker.get_slot("number"),
        )


class ActionFilterSubmit(Action):
    def name(self) -> Text:
        return "action_filter_submit"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:

        genre = tracker.get_slot("genre").lower()
        year_after = tracker.get_slot("year").lower()
        language = tracker.get_slot("language").lower()

        # Load dataframe top250
        df_top250 = pd.read_csv("top250.csv", sep=",")
        # use model to find the movie
        df_top250["Genre"] = df_top250["Genre"].str.lower()
        df_top250 = df_top250[df_top250["Genre"].str.contains(genre)]
        df_top250[["Year"]] = df_top250[["Year"]].apply(pd.to_numeric)
        df_top250 = df_top250[df_top250["Year"] > float(year_after)]
        df_top250["Language"] = df_top250["Language"].str.lower()
        df_top250 = df_top250[df_top250["Language"].str.contains(language)]

        # filtered out titles
        titles = ",".join([str(elem) for elem in df_top250["Title"]])
        # facebook messenger character limit per message is 640
        if len(titles) > 500:
            titles = titles[
                0:500
            ]  # safe because we have other message component like Genre
        else:
            titles = titles
        dispatcher.utter_message(
            template="utter_filter_thanks",
            Genre=tracker.get_slot("genre"),
            Year_after=tracker.get_slot("year"),
            Language=tracker.get_slot("language"),
            Titles=titles,
        )
        return []


class ActionMovieCluster(Action):
    def name(self) -> Text:
        return "action_movie_cluster"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        df_cluster = pd.read_csv("cluster_top250.csv", sep=",")

        # userMessage = next(tracker.get_latest_entity_values("movie"), None)
        # userMessage = tracker.get_latest_entity_values("movie")
        userMessage = tracker.latest_message["text"]
        # convert string representation of list to real list
        list_titles = []
        for i in range(len(df_cluster["titles"])):
            list_titles.append(ast.literal_eval(df_cluster["titles"][i]))
        # make the column of "titles" lower case and save it as "titles_list".
        # also strip away any spaces infront of each movie title
        list_lower_titles = []
        for i in range(len(df_cluster)):
            list_lower_titles.append([x.lower().strip() for x in list_titles[i]])
        # put it to a new column in the dataframe
        df_cluster["titles_list"] = list_lower_titles

        # split the inputs if there are more than one movie given
        # inputs = userMessage
        inputs = userMessage.lower()
        inputs = inputs.split('"')
        print("inputs", inputs)
        inputs = inputs[1].replace('"', "")
        # inputs = inputs.split('"')[0]
        inputs = inputs.split(",")

        # remove any empty spaces in the front of each titles
        inputs = [x.strip() for x in inputs]
        inputs = [i.lower() for i in inputs]
        print("inputs new", inputs)

        print(df_cluster)
        row_index = []
        for index in range(len(df_cluster)):
            i = set.intersection(set(inputs), set(df_cluster["titles_list"][index]))
            if len(i) > 0:
                row_index.append(index)

        # find the indexes of the columns with the movie names given by input
        filtered = df_cluster.loc[row_index, :]["titles"]
        titles = (
            ",".join([str(elem) for elem in filtered]).replace("[", "").replace("]", "")
        )
        # facebook messenger can only take max 640 characters. So I put 600 as safe figure
        if len(titles) > 600:
            titles = titles[0:600]
        else:
            titles = titles

        botResponse = f"I found the following movies: {titles}.".replace(
            "[", ""
        ).replace("]", "")
        dispatcher.utter_message(text=botResponse)
        return []


# class ActionMovieCluster(Action):
#     def name(self) -> Text:
#         return "action_movie_cluster"

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
#         df_cluster = pd.read_csv("cluster_top250.csv", sep=",")

#         userMessage = tracker.latest_message["text"]
#         # use model to find the movie
#         inputs = userMessage.split(",")
#         # merge data columns "keywords" and titles
#         df_cluster["merged_txt"] = df_cluster["keywords", "titles"]
#         df_cluster["merged_txt"] = df_cluster["merged_txt"].str.lower()
#         df_cluster['merged_txt'].replace(
#             "[", ""
#         ).replace("]", "")
#         df_cluster = df_cluster[df_cluster["merged_txt"].str.contains(inputs)]
#         # find the remaining "titles"
#         titles = ",".join([str(elem) for elem in df_cluster["title"]])

#         botResponse = f"I found the following movies: {titles}.".replace(
#             "[", ""
#         ).replace("]", "")
#         dispatcher.utter_message(text=botResponse)
#         return []

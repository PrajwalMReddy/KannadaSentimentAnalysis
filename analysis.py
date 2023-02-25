import os
import json

from nltk.sentiment import SentimentIntensityAnalyzer
from translate import Translator

minLikes = 10000000
maxLikes = 0

minReplies = 10000000
maxReplies = 0

minRetweets = 10000000
maxRetweets = 0


# Utility Method To Find All Politicians Whose Tweets Are Available
def get_politicians():
    path = "tweets-test"
    folders = [folder for folder in os.listdir(path) if os.path.isdir(os.path.join(path, folder))]

    for folder in folders:
        yield folder


# Utility Method To Find All The Available Tweets From A Given Politician
def get_politicians_tweets(politician):
    global maxLikes
    global minLikes

    global maxReplies
    global minReplies

    global maxRetweets
    global minRetweets

    path = f"tweets-test/{politician}"
    tweets = []

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)

        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding="utf-8") as file:
                data = json.load(file)

                if data["Likes"] > maxLikes:
                    maxLikes = data["Likes"]
                elif data["Likes"] < minLikes:
                    minLikes = data["Likes"]

                if data["Replies"] > maxReplies:
                    maxReplies = data["Replies"]
                elif data["Replies"] < minReplies:
                    minReplies = data["Replies"]

                if data["Retweets"] > maxRetweets:
                    maxRetweets = data["Retweets"]
                elif data["Retweets"] < minRetweets:
                    minRetweets = data["Retweets"]

                tweets.append(data)

    return tweets


def sentiment_polarity(text):
    sia = SentimentIntensityAnalyzer()

    score = sia.polarity_scores(text)
    key = list(score.keys())[list(score.values()).index(max(list(score.values())[:len(score) - 1]))]

    return score, key


def translate_text(json_tweet):
    if json_tweet["Language"] != "kn":
        return json_tweet["Tweet"]

    translator = Translator(to_lang="en")
    translation = translator.translate(json_tweet["Tweet"])

    return translation


def calculate_score(json_tweet):
    text = json_tweet["Tweet"]

    if json_tweet["Language"] != "en":
        text = translate_text(json_tweet)

    score, key = sentiment_polarity(text)

    # The Sentiment Polarity Is Worth 25% Of The Total Score
    # The Sentiment Polarity Also Cannot Be Negative
    sent_pol = (score["pos"] - score["neg"]) if (score["pos"] - score["neg"]) > 0 else 0

    likes_score = (json_tweet["Likes"] - minLikes) / (maxLikes - minLikes)  # Scales The Likes Score To The Range Of 0.0 to 1.0
    replies_score = (json_tweet["Replies"] - minReplies) / (maxReplies - minReplies)  # Scales The Replies Score To The Range Of 0.0 to 1.0
    retweets_score = (json_tweet["Retweets"] - minRetweets) / (maxRetweets - minRetweets)  # Scales The Retweets Score To The Range Of 0.0 to 1.0

    # The Final Total Score Is From 0.0 to 100.0
    total_score = 25 * (sent_pol + likes_score + replies_score + retweets_score)
    return total_score


def analyze_politician(politician):
    total_score = 0
    tweet_count = 0
    all_politicians_tweets = get_politicians_tweets(politician)

    for tweet in all_politicians_tweets:
        total_score += calculate_score(tweet)
        tweet_count += 1

    avg_score = total_score / tweet_count if tweet_count != 0 else 0

    return avg_score


def store_results(results):
    with open("./results.json", "w+") as file:
        json.dump(results, file)


def analyze():
    scores = {}
    all_politicians = get_politicians()

    while True:
        try:
            politician = next(all_politicians)
            scores.update({politician: analyze_politician(politician)})

        except StopIteration:
            break

    store_results(scores)


class CandidatePair:
    def __init__(self, candidate1, candidate2, predicted1, predicted2):
        self.candidate1 = candidate1
        self.candidate2 = candidate2
        self.predicted1 = predicted1
        self.predicted2 = predicted2

    def __repr__(self):
        return f"{self.candidate1}: {self.predicted1} | {self.candidate2}: {self.predicted2} {'✔️' if self.is_correct_prediction() else '❌'}"

    def is_correct_prediction(self):
        if self.predicted1 > self.predicted2:
            return True
        else:
            return False

    def margin_of_victory(self):
        return self.predicted1 - self.predicted2

    def percent_margin_of_victory(self):
        total = self.predicted1 + self.predicted2
        return ((self.predicted1 - self.predicted2) / total) * 100


def conclude():
    with open("./settings.json", 'r', encoding="utf-8") as file:
        settings = json.load(file)

    with open("./results.json", 'r', encoding="utf-8") as file:
        results = json.load(file)

    candidates = settings["Candidates"]
    candidatePairs = []

    for i in range(0, len(candidates), 2):
        if candidates[i]["Name"] in results.keys() and candidates[i + 1]["Name"] in results.keys():
            candidatePairs.append(
                CandidatePair(candidates[i]["Name"], candidates[i + 1]["Name"], results[candidates[i]["Name"]],
                              results[candidates[i + 1]["Name"]]))

    correct_predictions = 0
    total_predictions = len(candidatePairs)

    total_margin = 0
    total_percent_margin = 0

    print("All Predicted Pairs:")
    for pair in candidatePairs:
        print(pair)

        total_margin += pair.margin_of_victory()
        total_percent_margin += pair.percent_margin_of_victory()

        if pair.is_correct_prediction():
            correct_predictions += 1

    print(
        f"\nResults:\n"
        f"Total Correct Pairs: {correct_predictions}\n"
        f"Total Pairs: {total_predictions}\n"
        f"Average Net Margin: {(total_margin / total_predictions) if total_predictions != 0 else 0}\n"
        f"Average Percent Margin: {(total_percent_margin / total_predictions) if total_predictions != 0 else 0}%\n"
        f"Accuracy: {(correct_predictions / total_predictions) * 100 if total_predictions != 0 else 0}%"
    )


def main():
    analyze()
    conclude()


if __name__ == '__main__':
    main()

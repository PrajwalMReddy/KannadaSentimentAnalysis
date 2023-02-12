import json
import pathlib

import twint


def next_account():
    for account in open("accounts.txt", "r"):
        print(f"ACCOUNT: {account}")
        yield account.rstrip()


def store_tweets(tweets_dict_list):
    for tweet_dict in tweets_dict_list:
        pathlib.Path(f"tweets/{tweet_dict['Username']}").mkdir(parents=True, exist_ok=True)

        with open(f"tweets/{tweet_dict['Username']}/{tweet_dict['ID']}.json", "w+", encoding='utf8') as file:
            json.dump(tweet_dict, file, ensure_ascii=False)


def process_tweets(tweets_df):
    tweet_dict_list = []

    for index, row in tweets_df.iterrows():
        tweet_dict = {
            "ID": tweets_df.iat[index, 0],
            "Username": tweets_df.iat[index, 12],
            "Name": tweets_df.iat[index, 13],
            "Date": tweets_df.iat[index, 3],
            "Tweet": tweets_df.iat[index, 6],
            "Language": tweets_df.iat[index, 7],
            "Likes": int(tweets_df.iat[index, 22]),
            "Replies": int(tweets_df.iat[index, 23]),
            "Retweets": int(tweets_df.iat[index, 24]),
        }

        # print(tweet_dict)
        tweet_dict_list.append(tweet_dict)

    store_tweets(tweet_dict_list)


def scrape_users_tweets():
    all_accounts = next_account()

    while True:
        try:
            user = twint.Config()
            user.Limit = 1
            user.Username = next(all_accounts)
            user.Pandas = True

            try:
                twint.run.Search(user)
                tweets = twint.storage.panda.Tweets_df

                process_tweets(tweets)
                print("\n")

            except Exception:
                print(f"Error Retrieving Tweets From Account: {user.Username}")

        except StopIteration:
            break


scrape_users_tweets()

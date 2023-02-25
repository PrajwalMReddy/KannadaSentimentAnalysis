import json
import pathlib

import twint


def next_account():
    with open("settings.json", "r", encoding="utf-8") as file:
        settings = json.load(file)
        accounts = settings["Candidates"]

        for account in accounts:
            print(f"POLITICIAN: {account['Name']}")
            yield account['Account'].rstrip(), account['Name'].rstrip()


def get_dates():
    with open("settings.json", "r", encoding="utf-8") as file:
        settings = json.load(file)

        since = settings["Since"]
        until = settings["Until"]

        return since, until


def store_tweets(tweets_dict_list):
    for tweet_dict in tweets_dict_list:
        pathlib.Path(f"tweets-test/{tweet_dict['Name']}").mkdir(parents=True, exist_ok=True)

        with open(f"tweets-test/{tweet_dict['Name']}/{tweet_dict['ID']}.json", "w+", encoding='utf8') as file:
            # 'ensure_ascii=False' is to correctly handle tweets-test in the Kannada script
            json.dump(tweet_dict, file, ensure_ascii=False)


def process_tweets(tweets_df, politician_name):
    tweet_dict_list = []

    for index, row in tweets_df.iterrows():
        # Stores The Exact Features Required For The Data Analysis

        tweet_dict = {
            "ID": tweets_df.iat[index, 0],
            "Username": tweets_df.iat[index, 12],
            "Name": politician_name,
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
    since, until = get_dates()

    while True:
        try:
            user = twint.Config()

            user.Username, politician_name = next(all_accounts)
            user.Limit = 10000
            user.Pandas = True

            if since != "" and until != "":
                user.Since = since
                user.Until = until

            try:
                twint.run.Search(user)
                tweets = twint.storage.panda.Tweets_df

                process_tweets(tweets, politician_name)
                print("\n")

            except Exception:  # The Exact Exception Does Not Matter
                print(f"Error Retrieving Tweets From Account: {user.Username}\n\n")

        except StopIteration:
            break


def main():
    import time
    for i in range(100):
        scrape_users_tweets()
        time.sleep(5)


if __name__ == "__main__":
    main()

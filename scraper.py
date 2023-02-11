import twint


def next_account():
    for account in open("accounts.txt", "r"):
        print(f"ACCOUNT: {account}")
        yield account.rstrip()


def scrape_users_tweets():
    all_accounts = next_account()

    while True:
        try:
            user = twint.Config()
            user.Limit = 1
            user.Username = next(all_accounts)

            twint.run.Search(user)

            print("\n")

        except StopIteration:
            break


scrape_users_tweets()

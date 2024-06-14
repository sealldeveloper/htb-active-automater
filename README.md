# HTB Active Machines Threads Automater
This is a bot to get the current active HTB machines and make a forum channel with threads for easy access and communication between peers. This was made for the University CTF team I help administrate **MQCybersec**.

![image](https://github.com/sealldeveloper/htb-active-automater/assets/120470330/a80d964e-af9d-4bb5-8b75-9e95c3222088)


## .env Setup
Firstly, rename the `.env.template` to `.env`, here is a table for the key and value pairs that are expected.

| Key Name         | Value Type | Value Options | Optional? | Default Value | Purpose                                      |
|------------------|------------|---------------|-----------|---------------|----------------------------------------------|
| DISCORD_TOKEN    | String     | -             | No        | -             | The token for your Discord Bot.               |
| DISCORD_GUILD_ID | String     | -             | No        | -             | The ID for the Discord Server your bot is in. |
| HTB_API_TOKEN    | String     | -             | No        | -             | The HTB API Token generated [here](https://app.hackthebox.com/profile/settings). |

### How to get a HTB API Token

Go to [this url](https://app.hackthebox.com/profile/settings) when logged in. You should have a button to **Create App Token**, do so then set the value of the token to the generated token.

## Using the bot
This bot was designed on **Python 3.10.9** but <3.7 *should* function perfectly fine.

Firstly install the requirements:
```
python3 -m pip install -r requirements.txt
```

And then run the bot:
```
python3 main.py
```

## Notes
This bot was designed with the help of [HTB v4 API Documentation](https://github.com/Propolisa/htb-api-docs).

## To-do

## Known Bugs

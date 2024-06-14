# HTB Active Machines Threads Automater
This is a bot to get the current active HTB machines and make a forum channel with threads for easy access and communication between peers. This was made for the University CTF team I help administrate **MQCybersec**.

![image](https://github.com/sealldeveloper/htb-active-automater/assets/120470330/c3523f7a-df6c-4b91-8ab6-63f1f6d729ee)


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

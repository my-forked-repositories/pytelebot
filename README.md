# pytelebot
Telegram bot written in Python to control [Survaillance System](https://github.com/eliasxyz/homesentry).

## About
This Telegram Bot is used to control a remote surveillance system. Bot accepts updates from the system and passes queries to it. Bot has the following commands:
* `/register` - add remote surveillance system IP address. Bot will accepts updates from all systems at once;
* `/ping` - check if the remote surveillance system is responding;
* `/sentry` - start motion-detection module.

## Usage
Bot is meant to be hosted on Heroku cloud services, so it uses webhooks. To host bot locally, you need to comment out the following lines of code:

```
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
```

and uncomment `updater.start_polling()` line.

Install required dependencies - `pip install -r requirements.txt`

Now just run it - `python main.py`

On start bot will ask you for device's IP address. When you have submitted a valid IP address, you can start motion-detection module, and that's it!

## Example
Here is an example of how it works.

![TG Example](./examples/1.jpg?raw=true "TG_Example_1")

User starts conversation with the bot and enters device's valid IP address, checks if it's available and starts motion-detection module.

![TG Example](./examples/2.jpg?raw=true "TG_Example_1")

Bot receives frames with captured motion from the remote surveillance system.

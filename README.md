# Discoweb
A PyPi package that makes sending messages on Discord webhooks in Python easier and faster!

## What are Discord webhooks?
**Discord webhooks** are a feature in Discord that simplifies sending messages in a server without needing a bot, although, webhooks only send messages in the channel they were created in!

_(also dont worry this package has asynchronous support)_

## Installation
You can install this package via pip:
```bash
pip install discoweb
```

## Usage
### Basic text messages
First, create a webhook object using the **Webhook()** object:
```python
import discoweb

webhook = discoweb.Webhook("WEBHOOK_URL")
```
Then, to send a message, create a message object and then send the message using the webhook:
```python
import discoweb

webhook = discoweb.Webhook("WEBHOOK_URL")
message = discoweb.Message("funnybone")

webhook.send(message, username="Webhook")
# This will make the webhook send the message "funnybone" with the name "Webhook"!
```
### Rich Embeds, Files & Mention Control
Discoweb also supports Rich Embeds and files!
```python
import discoweb
webhook = discoweb.Webhook("WEBHOOK_URL")

# Beautiful embeds!
embed = (
    embedplus = discoweb.EmbedPlus(title='Rich Embed Test', description='This is a test for rich embeds!',
    image_url='IMAGE_URL', thumbnail_url='THUMBNAIL_URL')
    embedplus.setfooter(text='Discoweb Example', icon_url='ICON_URL')
    embedplus.setauthor(author='Discoweb', icon_url='ICON_URL', url='https://example.com')
)

# Local files (ex. images)!
catimage = discoweb.File('cat.png')
dogimage = discoweb.File('dog.jpeg')

# Mention control!
allowment = discoweb.AllowedMentions(
    everyone=False,
    users=False,
    roles=False
)

# And finally.. sending the message!
webhook.send(
    content='Hey guys, come look at this!',
    embeds=[embed],
    files=[catimage, dogimage],
    allowed_mentions=allowment
)
```
### Native Asynchronous Support!
Discoweb has asynchronous support too via aiohttp!
```python
import discoweb

async def main():
    # Create a webhook object!
    webhook = discoweb.AsyncHook('WEBHOOK_URL')
    
    # Send a message with it!
    await webhook.send(Message('Hello world!'))

    # Then close it!
    await webhook.close()
```
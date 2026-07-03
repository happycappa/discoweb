# Discoweb
A PyPi package that makes sending messages on Discord webhooks in Python easier and faster!

## What are Discord webhooks?
**Discord webhooks** are a feature in Discord that simplifies sending messages in a server without needing a bot, although, webhooks only send messages in the channel they were created in!

They make third party services be able to send you messages on Discord without requiring them to create a Discord bot!

# Usage
First, create a webhook object using the **Webhook()** object:
```python
import discoweb

webhook = discoweb.Webhook("WEBHOOK URL")
```
Then, to send a message, create a message object and then send the message using the webhook:
```python
import discoweb

webhook = discoweb.Webhook("WEBHOOK URL")
message = discoweb.Message("funnybone")

webhook.send(message, username="Webhook")
# This will make the webhook send the message "funnybone"!
```
If you instead pass in a _string_ instead of a message object in **webhook.send()**, it'll automatically create a new message object with the content being the string!
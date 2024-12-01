import json
import requests

def lambda_handler(event, context):
    # Extract the message from SNS event
    sns_message = event['Records'][0]['Sns']['Message']
    
    # Your bot token and chat ID
    bot_token = "REDACTED"
    chat_id = "REDACTED"

    # Send the message to Telegram
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": sns_message
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print(f"Telegram message sent: {sns_message}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram message: {e}")
        raise

    return {
        'statusCode': 200,
        'body': json.dumps('Notification sent to Telegram')
    }


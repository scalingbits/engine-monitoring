import boto3
import json  # json library imported
#
#   expects event parameter to contain:
#   {
#       "state.reported.rpm": 38,
#       "min_rpm": 30,
#       "notify_topic_arn": "arn:aws:sns:us-east-1:57EXAMPLE833:low-rpm-lambda"
#   }
#
#   sends a plain text string to be used in a text message
#
#      "Stirling engine {0} reports a low rpm {1}, which is below limit of {2}."
#
#   where:
#       {0} is the rpm value
#       {1} is the min_rpm value
#
def lambda_handler(event, context):

    # Create an SNS client to send notification
    sns = boto3.client('sns')

    # Format text message from data
    message_text = "Stirling engine reports a low rpm of {0}, which is below the limit of {1}.".format(
        str(event.get('state').get('reported').get('rpm')),
        str(event['min_rpm'])
    )
    # Publish the formatted message
    response = sns.publish(
        TopicArn = event['notify_topic_arn'],
        Message = message_text
    )

    return response
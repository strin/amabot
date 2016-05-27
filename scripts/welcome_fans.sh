curl -X POST -H "Content-Type: application/json" -d $'{
  "setting_type":"call_to_actions",
  "thread_state":"new_thread",
  "call_to_actions":[
    {
      "message":{
      "text":"Hey, there! I\'m Trump. Ask Me Anything! :P"
      }
    }
  ]
}' "https://graph.facebook.com/v2.6/1709532872618843/thread_settings?access_token=EAAYaEZA0ZCVM0BAOzNM7nzWznD7hqK4PkzIIm9YNzBhfeQvGSZBbqyl66Y9Jb6KYIZAMFuRXWerXOgHtmD5ajXd2wfZBhX887VZCZB0j4OOQtWxg9mWB5FjBhI8jDFlPfGj6NwDZBOTKZBZAs2KZA2DbTLqgd8Piy2XWkIVk4MQrNpwYYt5Lbv2eC1w"


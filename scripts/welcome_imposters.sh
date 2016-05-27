curl -X POST -H "Content-Type: application/json" -d $'{
  "setting_type":"call_to_actions",
  "thread_state":"new_thread",
  "call_to_actions":[
    {
      "message":{
      "text":"Hey, there! Have you ever wondered what\'s it like to be a celebrity? In this game, you act to be a celebrity\'s imposter. Let\'s see how many fans you can fool :)"
      }
    }
  ]
}' "https://graph.facebook.com/v2.6/1033841673375305/thread_settings?access_token=EAAYaEZA0ZCVM0BAGOqt1rK6Q3tQmnbRxqVqkWfvwCWWlXBlvJIFHsq9WOOmTeuZCRg6BFMnHTx1GeLbmgRk790R2M7Jprlc6MkBf4SRsrPhAiQhJVzyxlZCpAQRLR9cHuKNvfEC7wVrbMsSe2ybxE4p2lq6C9wS4eMgd59xC32B0UD3HkQMC"


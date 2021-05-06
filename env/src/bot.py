import slack
import os
import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

from flask import Flask, request, make_response, Response, jsonify

from slack.web.client import WebClient
from slack.errors import SlackApiError
from slack.signature import SignatureVerifier

from slackeventsapi import SlackEventAdapter

from business import *
from error import *
import data

load_dotenv()
OAUTH_TOKEN = os.environ["OAUTH_TOKEN"]
SIGNING_SECRET = os.environ["SIGNING_SECRET"]
client = WebClient(OAUTH_TOKEN)
verifier = SignatureVerifier(SIGNING_SECRET)
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, "/slack/events", app)

@app.route("/test", methods=["GET"])
def test():
    return jsonify(data.channel_members["C01URDTNF3N"]["members"])

# slash command : view eligibles
@app.route("/slack/view", methods=["POST"])
def view():
    try:
        info = validate(verifier, request)
        channel_id = info["channel_id"]
        user_id = info["user_id"]
        if channel_id not in data.channel_members or "members" not in data.channel_members[channel_id]:
            text = ":cry: Channel data not found. Reinitiate."
        else:    
            members = data.channel_members[channel_id]["members"]
            current = data.channel_members[channel_id]["current"]
            text = extract_member_ids_string(members, current)
        response = client.chat_postEphemeral(
            channel=channel_id, user=user_id, text=text, attachments=[]
        )
    except InvalidRequest as e:
        msg = "Invalid Request"
        log(e, msg)
        return make_response(msg, 403)
    except SlackApiError as e:
        msg = "Request to Slack API Failed"
        log(e, msg)
        return make_response("", e.response.status_code)
    except: # catch *all* exceptions
        e = sys.exc_info()[0]
        log(e, msg)
        return make_response("", 400)
    return make_response("", response.status_code)

# slash command : add user(s)
@app.route("/slack/add", methods=["POST"])
def add():
    try:
        info = validate(verifier, request)
        channel_id = info["channel_id"]
        user_id = info["user_id"]
        text = info["text"]

        if channel_id not in data.channel_members or "members" not in data.channel_members[channel_id]:
            text = ":cry: Channel data not found. Reinitiate."
        else: 
            members = data.channel_members[channel_id]["members"]
            result, success = add_users_by_name(text, members)
            if success:
                text = f'<@{user_id}> added "{text}" :white_check_mark:'
                data.channel_members[channel_id]["members"] = result
            else:
                text = f'<@{user_id}>, :cry: "{text}"\n Reason: {result}'

        response = client.chat_postMessage(channel=channel_id, text=text)
    except InvalidRequest as e:
        msg = "Invalid Request"
        log(e, msg)
        return make_response(msg, 403)
    except SlackApiError as e:
        msg = "Request to Slack API Failed"
        log(e, msg)
        return make_response("", e.response.status_code)
    except: # catch *all* exceptions
        e = sys.exc_info()[0]
        log(e, msg)
        return make_response("", 400)
    return make_response("", response.status_code)

# slash command : remove user(s)
@app.route("/slack/remove", methods=["POST"])
def remove():
    try:
        info = validate(verifier, request)
        channel_id = info["channel_id"]
        user_id = info["user_id"]
        text = info["text"]
        if channel_id not in data.channel_members or "members" not in data.channel_members[channel_id]:
            text = ":cry: Channel data not found. Reinitiate."
        else:
            members = data.channel_members[channel_id]["members"]
            result, success = remove_users_by_name(text, members)

            if success:
                text = f'<@{user_id}> deleted "{text}" :white_check_mark:'
                data.channel_members[channel_id]["members"] = result
            else:
                text = f'<@{user_id}>, :cry: "{text}"\n Reason: {result}'
        response = client.chat_postMessage(channel=channel_id, text=text)
    except InvalidRequest as e:
        msg = "Invalid Request"
        log(e, msg)
        return make_response(msg, 403)
    except SlackApiError as e:
        msg = "Request to Slack API Failed"
        log(e, msg)
        return make_response("", e.response.status_code)
    except: # catch *all* exceptions
        e = sys.exc_info()[0]
        log(e, msg)
        return make_response("", 400)
    return make_response("", response.status_code)

# slash command : swap two users
@app.route("/slack/swap", methods=["POST"])
def swap():
    try:
        info = validate(verifier, request)
        channel_id = info["channel_id"]
        user_id = info["user_id"]
        text = info["text"]
        if channel_id not in data.channel_members or "members" not in data.channel_members[channel_id]:
            text = ":cry: Channel data not found. Reinitiate."
        else:
            members = data.channel_members[channel_id]["members"]
            result, success = swap_users_by_name(text, members)

            if success:
                text = f'<@{user_id}> swapped "{text}" :white_check_mark:'
                data.channel_members[channel_id]["members"] = result
            else:
                text = f'<@{user_id}>, :cry: "{text}"\n Reason: {result}'
        response = client.chat_postMessage(channel=channel_id, text=text)
    except InvalidRequest as e:
        msg = "Invalid Request"
        log(e, msg)
        return make_response(msg, 403)
    except SlackApiError as e:
        msg = "Request to Slack API Failed"
        log(e, msg)
        return make_response("", e.response.status_code)
    except: # catch *all* exceptions
        e = sys.exc_info()[0]
        log(e, msg)
        return make_response("", 400)
    return make_response("", response.status_code)

# slash command : skip to next eligible from current person assigned role
@app.route("/slack/skip", methods=["POST"])
def skip():
    try:
        info = validate(verifier, request)
        channel_id = info["channel_id"]
        user_id = info["user_id"]
        text = info["text"]
        if channel_id not in data.channel_members or "current" not in data.channel_members[channel_id] or "members" not in data.channel_members[channel_id]:
            text = ":cry: Channel data not found. Reinitiate."
        else:
            members = data.channel_members[channel_id]["members"]
            members_length = len(members)
            current = data.channel_members[channel_id]["current"]
            n_current = skipCurrentUser(text, current, members_length)
            text = f'<@{user_id}> skipped by "{text}" :white_check_mark:'
            if n_current != current:
                rest_of_topic, name = form_conversation_topic(channel_id)
                topic = rest_of_topic + f'SCRUM:<@{members[n_current]["id"]}>'
                client.conversations_setTopic(channel=channel_id,topic=topic)

            data.channel_members[channel_id]["current"] = n_current
        
        response = client.chat_postMessage(channel=channel_id, text=text)
    except InvalidRequest as e:
        msg = "Invalid Request"
        log(e, msg)
        return make_response(msg, 403)
    except SlackApiError as e:
        msg = "Request to Slack API Failed"
        log(e, msg)
        return make_response("", e.response.status_code)
    except: # catch *all* exceptions
        e = sys.exc_info()[0]
        log(e, msg)
        return make_response("", 400)
    return make_response("", response.status_code)

@slack_event_adapter.on("app_mention")
def app_mention(payload):
    try:
        event = payload.get("event", {})
        text = event.get("text", {})
        channel_id = event.get("channel")
        if "init" in text or "reset" in text:
            members = filter_conversation_members_list(channel_id)
            
            rest_of_topic, name = form_conversation_topic(channel_id)
            current = form_current_index(name, members)
            data.channel_members[channel_id] = {"members": members, "current": current}
            member_id = members[current]['id']
            topic = rest_of_topic + f'SCRUM:<@{member_id}>'
            if current == 0:
                client.conversations_setTopic(channel=channel_id,topic=topic)

            client.chat_postMessage(
                channel=channel_id,
                text=f"Our scrum master is <@{member_id}> :tada:\nAll remaining {len(members)-1} members are eligible in next sprints.",
            )
            
        if "next" in text or "skip" in text:
            members = data.channel_members[channel_id]["members"]
            members_length = len(members)
            current = data.channel_members[channel_id]["current"]
            n_current = skipCurrentUser('', current, members_length)
            if n_current != current:
                rest_of_topic, name = form_conversation_topic(channel_id)
                topic = rest_of_topic + f'SCRUM:<@{members[n_current]["id"]}>'
                client.conversations_setTopic(channel=channel_id,topic=topic)
            data.channel_members[channel_id]["current"] = n_current

    except: # catch *all* exceptions
        e = sys.exc_info()[0]
        log(e, "Slack event API failed")
        client.chat_postMessage(
            channel=channel_id, text=f"Something went wrong. Try again later!"
        )


def get_conversation_topic(channel_id):
    api_method = "conversations.info"
    params = {"channel": channel_id, "pretty": 1}
    try:
        response = client.api_call(api_method, http_verb='GET', params=params)
        if response.status_code == 200:
            return response["channel"]["topic"]["value"]
        else:
            return ''
    except SlackApiError as e:
        return e

def get_conversation_members(channel_id):
    api_method = "conversations.members"
    params = {"channel": channel_id, "pretty": 1}

    try:
        response = client.api_call(api_method, http_verb='GET', params=params)
        if response.status_code == 200:
            return response["members"]
        else:
            return []
    except Exception as e:
        return e
        
def get_users_list():
    api_method = "users.list"
    try:
        response = client.api_call(api_method, http_verb='GET')
        if response.status_code == 200:
            return response["members"]
        else:
            return []
    except Exception as e:
        return e
#print(get_users_list()) #'C01URDTNF3N'
def validate(verifier, request):
    if not verifier.is_valid_request(request.get_data(), request.headers):
        raise InvalidRequest
    return request.form
def log(e, msg=""):
    if len(msg) > 0:
        logging.error(f"{msg}: {e.response.status_code}.")
        logging.error(e.response)
    else:
        logging.error(f"Unknown error: {e}.")


# Start the Flask server
if __name__ == "__main__":
    app.run()


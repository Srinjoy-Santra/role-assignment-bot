from bot import *
import re

def form_conversation_topic(channel_id):
    topic = get_conversation_topic(channel_id)
    return topic.split('SCRUM:')

def form_current_index(name, members):
    current = 0
    for idx, member in enumerate(members):
        if member['name'] is name:
            current=idx
    return current

def filter_conversation_members_list(channel_id):
    try:
        conversation_members = get_conversation_members(channel_id)
        users = get_users_list()

        members = list(filter(lambda user: user["id"] in conversation_members, users))
        return members
    except Exception as e:
        return e


def extract_member_ids_string(members, current):
    output = "The members are:\n"
    print('current',current)
    for id, member in enumerate(members):
        if id is current:
            status = ':calendar:'
        else:
            status = ':zzz:'
        output += f"{id}. <@{member['id']}> {status}\n"
    return output


def convert_text_to_names(text):
    text = text.strip()
    names = text[1:].split("@")
    names = [name.strip() for name in names]
    return names


def convert_names_to_ids(names, users):

    members = list(filter(lambda user: user if user["name"] in names else None, users))
    ids = [member["id"] for member in members]
    print(names, ids)
    return ids


def add_users_by_name(text, members):
    names = convert_text_to_names(text)
    users = get_users_list()
    ids = convert_names_to_ids(names, users)
    member_ids = [member["id"] for member in members]

    if not set(ids).issubset(member_ids):
        ids = [x for x in ids if not x in member_ids]
        new_members = list(filter(lambda user: user["id"] in ids, users))
        members += new_members
        return (members, True)
    else:
        return('Members are already present', False)
    
    return ('Something went wrong', False)


def remove_users_by_name(text, members):
    names = convert_text_to_names(text)
    member_names = [member["name"] for member in members]

    if set(names).issubset(member_names):
        members = list(filter(lambda member: member["name"] not in names, members))
        return (members, True)
    else:
        return ('Members are already not present',False)

    return ('Something went wrong', False)


def swap_users_by_name(text, members):
    names = convert_text_to_names(text)
    if len(names) > 2:
        return ("Cannot swap more than 2 users", False)

    name_1, name_2 = names
    member_names = [member['name'] for member in members]
    if name_1 not in member_names or name_2 not in member_names:
        return ("One of the names was wrong", False)

    a, b = member_names.index(name_1), member_names.index(name_2)
    members[a], members[b] = members[b], members[a]

    return (members, True)

def skipCurrentUser(text, current, length):
    try:
        skipBy = int(text)
        return (current + skipBy)%length
    except:
        return (current + 1)%length

#print(form_conversation_topic('C01URDTNF3N', members))
'''
r,s = swap_users_by_name("@srinjoy.santra @scrum_mastery", members)
if s:
    print([member['name'] for member in r])

'''
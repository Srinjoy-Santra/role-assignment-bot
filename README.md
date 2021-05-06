# Role Assignment Bot

> A slackbot to deteremine who will be the next iteration manager (or, scrum master, roster)

Also, suggest a better name! e.g. `@scrumbot`

## Usecases

- Obtain the list of active members in a group and put it in the queue. `@scrumbot init`
- Determine who all are eligible to be scrum master.
  - Will be a manual process (with `/!add` or `/!remove`)
- Rotate among elgible active members biweekly / sprint duration.
  - Round Robin strategy seems applicable. 
  - A reminder to the bot instead of scheduling it. `/remind #channel "@scrumbot skip" for every other Friday at 6:00pm`
- Change the description to edit the present scrum master.

### Edge cases

> Not handled yet!

- What happens if sprint ends early? (1 week)
  - Find possibilities to obtain the exact sprint duration from JIRA. (can be too much of a hassle!!)
- What happens if an assignee wants to replace his/her duty with another member for the sprint?
    - How many times can he/she replace?
    - Need affirmations from both the assigned and the assignee.

## Commands

- `/!add @user1 @user2 ...` = add user(s) eligible to be scrum master in a channel
- `/!remove @user1 @user2 ...` = remove user(s) eligible to be scrum master in a channel
- `/!swap @user1 @user2` = swap user1's turn with user2 for one iteration
- `/!view` = show current scrum master, followed by others in line
- `/!skip` = pre-empt current scrum master's turn, and appoint the next eligible
- `/!skip n` = skip to the nth member

## Schema

```js
[
  channel_id:
  {
    members: [{
      name: 'srinjoy.santra',
      email: '',
      // .... basically how slack returns users.list data
    }

    ],
    current: 1
  },
  channel_id2:
]
```


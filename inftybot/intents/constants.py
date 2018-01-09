# coding: utf-8

TOPIC_TYPE_NEED = 0
TOPIC_TYPE_GOAL = 1
TOPIC_TYPE_IDEA = 2
TOPIC_TYPE_PLAN = 3
TOPIC_TYPE_STEP = 4
TOPIC_TYPE_TASK = 5

TOPIC_TYPE_CHOICES = {
    TOPIC_TYPE_NEED: 'Need',
    TOPIC_TYPE_GOAL: 'Goal',
    TOPIC_TYPE_IDEA: 'Idea',
    TOPIC_TYPE_PLAN: 'Plan',
    TOPIC_TYPE_STEP: 'Step',
    TOPIC_TYPE_TASK: 'Task'
}

TOPIC_PART_TYPE = 'type'
TOPIC_PART_TITLE = 'title'
TOPIC_PART_BODY = 'body'
TOPIC_PART_CATEGORY = 'category'

TOPIC_PART_CHOIES = (
    (TOPIC_PART_TYPE, 'Type'),
    (TOPIC_PART_TITLE, 'Title'),
    (TOPIC_PART_BODY, 'Body'),
    (TOPIC_PART_CATEGORY, 'Category'),
)

CURRENT_TOPIC = 'current'
NEXT_PAGE = 'next-page'
PREV_PAGE = 'prev-page'

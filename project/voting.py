import random

def generate_random_survey(sug_list_songs):
    num_choices = len(sug_list_songs)
    num_shown = 2

    choice_list = randomize_choices(num_choices, num_shown)

    ret = []

    for i in choice_list:
        ret.append(sug_list_songs[i])

    return ret

def randomize_choices(num_choices, num_shown):
    poss_choices = set([])
    for i in range(0, num_choices):
        choice = ChoiceRepr(i)
        poss_choices.add(choice)

    choice_list = []
    
    while len(poss_choices) > 3:
        random_choice = random.sample(poss_choices, 4)
        for choice in random_choice:
            choice_list.append(choice.id)
            choice.times_used += 1
            
            if choice.times_used >= num_shown:
                poss_choices.remove(choice)

    return choice_list

class ChoiceRepr():
    id = 0
    times_used = 0

    def __init__(self, id):
        self.id = id

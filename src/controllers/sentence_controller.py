from src.controllers.validators import validate_gloss

def generate_tsl(gloss):
    if not validate_gloss(gloss):
        return
    print(gloss)


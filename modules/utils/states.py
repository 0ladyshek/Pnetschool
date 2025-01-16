from aiogram.dispatcher.filters.state import State, StatesGroup

class Register(StatesGroup):
    url = State()
    username = State()
    password = State() 
    school = State()
    
class Schedule(StatesGroup):
    date = State()
    
class Homework(StatesGroup):
    date = State()
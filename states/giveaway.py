from aiogram.fsm.state import State, StatesGroup


class EditGiveawayStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_response = State()


class SetChannelStates(StatesGroup):
    waiting_for_channel = State()
    waiting_for_text = State()

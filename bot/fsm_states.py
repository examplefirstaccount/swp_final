from aiogram.filters.state import StatesGroup, State


class RecurringAddingState(StatesGroup):
    EnterRecurringTitle = State()
    EnterRecurringPeriod = State()
    EnterRecurringExpression = State()
    EnterRecurringMessage = State()
    data = State()

from aiogram.filters.state import State, StatesGroup


class IntervalEditingState(StatesGroup):
    EnterNewInterval = State()


class RecurringAddingState(StatesGroup):
    EnterRecurringTitle = State()
    EnterRecurringPeriod = State()
    EnterRecurringExpression = State()
    EnterRecurringMessage = State()

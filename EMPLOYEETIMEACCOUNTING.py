"""
todo
Глобальные предложения по оптимизации:
1) Не везде соблюдается PEP8, код читать тяжело. Можно использовать линтеры, напр. flake8 и black
2) Не хватает типизации кода
3) Не хватает обработки ошибок
"""

# Import necessary system classes
from System import DayOfWeek, DateTimeKind

# Define constants for entity types and attributes
TIMERANGE_TYPE = 'TIMERANGE'
EMPLOYEE_TYPE = 'EMPLOYEE'
DayActivity = 'DAILY_ACTIVITY'
DayActivityToEmployeeRef = 'DAILYACTIVITYTOEMPLOYEE'
WeeklyActivity = 'WEEKLY_ACTIVITY'
WeekActivityToEmployeeRef = 'WEEKLYACTIVITYTOEMPLOYEE'
MonthlyActivity = 'MONTHLY_ACTIVITY'
MonthActivityToEmployeeRef = 'MONTHLYACTIVITYTOEMPLOYEE'
FromAttribute = 'FROM'
ToAttribute = 'TO'
DateAttribute = 'DATE'
HoursWorked = 'HOURS_WORKED'
TIMEZONE_ATTR = 'TIMEZONE'
TIMERANGE_TO_EMPLOYEE_REF = 'EMPLOYEEFROMTIMERANGE'


class Week:
    """
    Class to represent a week with a start and end date
    """

    def __init__(self, weekStart, weekEnd):
        self.weekStart = weekStart
        self.weekEnd = weekEnd

    def __str__(self):
        return f'Week start: {self.weekStart} - Week end {self.weekEnd}'


class Month:
    """
    Class to represent a month with a start and end date
    """

    def __init__(self, monthStart, monthEnd):
        self.monthStart = monthStart
        self.monthEnd = monthEnd

    def __str__(self):
        return f'Month start: {self.monthStart} - Month end {self.monthEnd}'


def _GetWeek(time):
    """
    Function to calculate the week containing the given date
    It ensures the week is complete by including surrounding days from adjacent months
    """

    # Generate a list of all dates in the current month
    dates = range(1, DateTime.DaysInMonth(time.Year, time.Month) + 1).Select(
        lambda n: DateTime(time.Year, time.Month, n, 0, 0, 0, DateTimeKind.Utc)).ToList()

    # Calculate the number of days in the previous month
    daysInPreviousMonth = DateTime.DaysInMonth(time.Year, time.AddMonths(-1).Month)
    # Generate dates for the last 7 days of the previous month
    previousMonthDates = range(daysInPreviousMonth, daysInPreviousMonth - 7, -1).Select(
        lambda n: DateTime(time.Year, time.AddMonths(-1).Month, n, 0, 0, 0, DateTimeKind.Utc)).ToList()
    # Combine the dates from the current and previous months
    previousMonthDates.AddRange(dates)
    # Generate the first 6 dates of the next month
    nextMonthDates = range(1, 7).Select(
        lambda n: DateTime(time.Year, time.Month + 1, n, 0, 0, 0, DateTimeKind.Utc)).ToList()
    # Add the next month's dates to the combined list
    previousMonthDates.AddRange(nextMonthDates)

    # Log all the dates considered for the week calculation
    outp_dates = previousMonthDates
    log(f'{outp_dates}')

    # Find the last Monday before or on the given date to mark the start of the week
    weekStart = outp_dates.Last(lambda d: d.DayOfWeek == DayOfWeek.Monday and d <= time)
    # Find the first Sunday after the weekStart to mark the end of the week
    weekEnd = outp_dates.First(lambda d: weekStart < d and d.DayOfWeek == DayOfWeek.Sunday)

    # Return a Week object with the calculated start and end dates
    return Week(weekStart, weekEnd)


def _GetMonth(time):
    """
    Function to calculate the month containing the given date
    """
    # Generate a list of all dates in the current month
    dates = range(1, DateTime.DaysInMonth(time.Year, time.Month) + 1).Select(
        lambda n: DateTime(time.Year, time.Month, n, 0, 0, 0, DateTimeKind.Utc)).ToArray()
    # Return a Month object with the first and last dates of the month
    return Month(dates.First(), dates.Last())


# Parse entity ID from context parameters and log it for debugging
timeRangeEntityId = Guid.Parse(str(context.ActionParameters['entityId']))
log(f'Time range entity id: {timeRangeEntityId}')

# Parse 'from' date value from context parameters and log it for debugging
valueFrom = DateTime.Parse(context.ActionParameters['from'].ToString('O'), None, DateTimeStyles.AdjustToUniversal)
log(f'From value: {str(valueFrom)}')

# Parse 'to' date value from context parameters and log it for debugging
valueTo = DateTime.Parse(context.ActionParameters['to'].ToString('O'), None, DateTimeStyles.AdjustToUniversal)
log(f'To value: {str(valueTo)}')

# Determine if subtraction is required based on context parameters
isSubtract = str(context.ActionParameters['isSubtract'])
if isSubtract == 'TRUE':
    isSubtract = True
else:
    isSubtract = False

# Retrieve the time range entity by its ID
timeRangeEntity = find(entitiesQuery(
    locale='fake',
    entitiesByIds=[timeRangeEntityId],
    entitiesByEntityTypeKeys=[TIMERANGE_TYPE],
    entitiesOptions=entitiesOptions(
        includeReferences=True
    ))).SingleOrDefault()

# Check if the time range entity was found
if timeRangeEntity is None:
    raise ValueError(f'Can not find TimeRange entity with id {timeRangeEntityId}')

# Get the employee entity ID from the references of the time range entity
employeeEntityId = timeRangeEntity.references.Single().Value[0].toEntityId
log(f'Found time range: {timeRangeEntity.id} with employee {employeeEntityId}')

# Retrieve the employee entity by its ID
employeeEntity = find(entitiesQuery(
    entitiesByIds=[employeeEntityId],
    entitiesByEntityTypeKeys=[EMPLOYEE_TYPE],
    entitiesOptions=entitiesOptions(
        includeAttributeValuesByAttributeKeys=[TIMEZONE_ATTR]
    )))[0]

# Attempt to get the employee's timezone from attributes
try:
    employeesOrgTimezone = int(employeeEntity.attributes[TIMEZONE_ATTR].localizedValues[None].value)
except:
    employeesOrgTimezone = 0

# Set the global variable TODAY with consideration of the employee's timezone
# todo Без global тут можно обойтись
global TODAY

# Apply timezone offset to the 'from' date
TODAY = valueFrom.AddHours(employeesOrgTimezone).Date
log(f'Employee local date={TODAY}')

# Get the week that contains today's date
week = _GetWeek(TODAY)
log(f'Week: {str(week)}')

# Get the month that contains today's date
month = _GetMonth(TODAY)
log(f'Month: {str(month)}')

# Find activities related to the employee within the specified time range
entities = find(entitiesQuery(
    locale='fake',
    entitiesByReferencedTo=[referencedToQueryFilter(entityId=employeeEntityId)],
    entitiesByEntityTypeKeys=[DayActivity, WeeklyActivity, MonthlyActivity],
    entitiesOptions=entitiesOptions(
        includeReferences=True,
        includeAttributeValuesByAttributeKeys=['*']
    )))

# Calculate the amount of work in the specified time range
workAmount = valueTo - valueFrom
if isSubtract == True:
    workAmount = -workAmount
log(f'Work amount: {workAmount}')


def _CheckDayActivity(attributes):
    """
    Check if the activity date matches today's date.
    """
    dayActivityDate = DateTime.Parse(None if attributes[DateAttribute].localizedValues[None].value is None else
                                     attributes[DateAttribute].localizedValues[None].value)
    return dayActivityDate == TODAY


def _GetDayActivity(entities):
    """
    Retrieve daily activity from the list of activities.
    """
    log('Try to get daily activity')
    # Filter for daily activities
    dayActivities = entities.Where(lambda entity: entity.type == DayActivity).ToArray()

    if dayActivities.Length == 0:
        return None

    # Return first daily activity matching today's date
    # todo Нет необходимости приводить filter к list и iter, возвращаемый из filter объект уже является итератором
    return next(iter(list(filter(lambda entity: _CheckDayActivity(entity.attributes), dayActivities))), None)


# Get daily activity
dailyActivity = _GetDayActivity(entities)
if dailyActivity is None:
    log('Daily activity is not found')
else:
    log(f'Daily activity is found {dailyActivity.id}')


def _CheckWeeklyActivity(attributes):
    """
    Check if the activity falls within the current week.
    """
    value = None if attributes[FromAttribute].localizedValues[None].value is None else \
        attributes[FromAttribute].localizedValues[None].value
    weeklyStart = DateTime.Parse(value) >= week.weekStart

    # todo Код дублируется
    value = None if attributes[ToAttribute].localizedValues[None].value is None else \
        attributes[ToAttribute].localizedValues[None].value
    weeklyEnd = DateTime.Parse(value) <= week.weekEnd

    return weeklyStart and weeklyEnd


def _GetWeeklyActivity(entities):
    """
    Retrieve weekly activity from the list of activities.
    """
    log('Try to get weekly activity')
    weeklyActivities = entities.Where(lambda entity: entity.type == WeeklyActivity).ToArray()

    if weeklyActivities.Length == 0:
        return None

    # todo Нет необходимости приводить filter к list и iter, возвращаемый из filter объект уже является итератором
    return next(iter(list(filter(lambda entity: _CheckWeeklyActivity(entity.attributes), weeklyActivities))), None)


# Retrieve the weekly activity from the list of entities
weeklyActivity = _GetWeeklyActivity(entities)
# Check if a weekly activity was found
if weeklyActivity is None:
    log('Weekly activity is not found')
else:
    log(f'Weekly activity is found {weeklyActivity.id}')


def _CheckMonthlyActivity(attributes):
    """
    Check if the activity falls within the current month.
    """
    # Get the 'From' date value and check if it is greater than or equal to the month's start date
    value = None if attributes[FromAttribute].localizedValues[None].value is None else \
        attributes[FromAttribute].localizedValues[None].value
    monthStart = DateTime.Parse(value) >= month.monthStart

    # todo Код дублируется
    value = None if attributes[ToAttribute].localizedValues[None].value is None else \
        attributes[ToAttribute].localizedValues[None].value
    monthEnd = DateTime.Parse(value) <= month.monthEnd

    return monthStart and monthEnd


def _GetMonthlyActivity(entities):
    """
    Retrieve monthly activity from the list of activities.
    todo Функции _GetMonthlyActivity, _GetWeeklyActivity, _GetDayActivity имеют схожую логику, можно в одну функцию
    """
    log('Try to get monthly activity')
    monthlyActivities = entities.Where(lambda entity: entity.type == MonthlyActivity).ToArray()
    if monthlyActivities.Length == 0:
        return None

    # todo Нет необходимости приводить filter к list и iter, возвращаемый из filter объект уже является итератором
    return next(iter(list(filter(lambda entity: _CheckMonthlyActivity(entity.attributes), monthlyActivities))), None)

# Get the monthly activity from the entities
monthlyActivity = _GetMonthlyActivity(entities)
if monthlyActivity is None:
    log('Monthly activity is not found')
else:
    log(f'Monthly activity is found {monthlyActivity.id}')


def addOrUpdateAttribute(entity, attributeKey, value, isAdd):
    """
    Add or update an attribute of an entity based on the isAdd flag.
    """
    if isAdd == True:
        entity.addAttribute(attributeKey, None, valueLocale(value=value, display=value))
    elif isAdd == False:
        entity.updateAttribute(attributeKey, None, valueLocale(value=value, display=value))


def addEntityReference(entity, referenceKey, toEntityId):
    """
    Add a reference from one entity to another.
    """
    entity.addReference(referenceKey, toEntityId)


def format_string(timespan):
    """
    Format a TimeSpan object into a string representation.
    """
    newTs = timespan.ToString("d\.hh\:mm\:ss")
    if TimeSpan.Zero > timespan:
        newTs = '-' + newTs
    return newTs

# Format the work amount into a string for logging
workAmountValue = format_string(workAmount)
log(f'This timerange workAmount={workAmountValue}')

# todo Код в каждом блоке дублируется, меняется только текст логгера и условие. Можно вынести в функцию, чтобы избежать дублирования.
# Check if daily activity exists; if not, create a new one
if dailyActivity is None:
    createdDailyActivity = create(DayActivity)
    addOrUpdateAttribute(createdDailyActivity, HoursWorked, workAmountValue, True)
    addOrUpdateAttribute(createdDailyActivity, DateAttribute, TODAY.ToString('O'), True)
    addEntityReference(createdDailyActivity, DayActivityToEmployeeRef, employeeEntityId)
else:
    currentAmount = TimeSpan.Parse(dailyActivity.attributes[HoursWorked].localizedValues[None].value)
    currentAmount += workAmount
    currentAmountValue = format_string(currentAmount)
    log(f'Daily new amount={currentAmountValue}')
    addOrUpdateAttribute(dailyActivity, HoursWorked, currentAmountValue, False)

# Check if weekly activity exists; if not, create a new one
if weeklyActivity is None:
    createdWeeklyActivity = create(WeeklyActivity)
    addOrUpdateAttribute(createdWeeklyActivity, HoursWorked, workAmountValue, True)
    addOrUpdateAttribute(createdWeeklyActivity, FromAttribute, week.weekStart.Date.ToString('O'), True)
    addOrUpdateAttribute(createdWeeklyActivity, ToAttribute, week.weekEnd.Date.ToString('O'), True)
    addEntityReference(createdWeeklyActivity, WeekActivityToEmployeeRef, employeeEntityId)
else:
    currentAmount = TimeSpan.Parse(weeklyActivity.attributes[HoursWorked].localizedValues[None].value)
    currentAmount += workAmount
    currentAmountValue = format_string(currentAmount)
    log(f'Weekly new amount={currentAmountValue}')
    addOrUpdateAttribute(weeklyActivity, HoursWorked, currentAmountValue, False)

# Check if monthly activity exists; if not, create a new one
if monthlyActivity is None:
    createdMonthlyActivity = create(MonthlyActivity)
    addOrUpdateAttribute(createdMonthlyActivity, HoursWorked, workAmountValue, True)
    addOrUpdateAttribute(createdMonthlyActivity, FromAttribute, month.monthStart.Date.ToString('O'), True)
    addOrUpdateAttribute(createdMonthlyActivity, ToAttribute, month.monthEnd.Date.ToString('O'), True)
    addEntityReference(createdMonthlyActivity, MonthActivityToEmployeeRef, employeeEntityId)
else:
    currentAmount = TimeSpan.Parse(monthlyActivity.attributes[HoursWorked].localizedValues[None].value)
    currentAmount += workAmount
    currentAmountValue = format_string(currentAmount)
    log(f'Monthly new amount={currentAmountValue}')
    addOrUpdateAttribute(monthlyActivity, HoursWorked, currentAmountValue, False)

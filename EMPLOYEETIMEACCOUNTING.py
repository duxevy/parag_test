from System import DayOfWeek, DateTimeKind

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
    def __init__(self, weekStart, weekEnd):
        self.weekStart = weekStart
        self.weekEnd = weekEnd

    def __str__(self):
        return f'Week start: {self.weekStart} - Week end {self.weekEnd}'

class Month:
    def __init__(self, monthStart, monthEnd):
        self.monthStart = monthStart
        self.monthEnd = monthEnd

    def __str__(self):
        return f'Month start: {self.monthStart} - Month end {self.monthEnd}'

def _GetWeek(time):
    dates = range(1, DateTime.DaysInMonth(time.Year, time.Month) + 1).Select(lambda n: DateTime(time.Year, time.Month, n, 0, 0, 0, DateTimeKind.Utc)).ToList()
    
    daysInPreviousMonth = DateTime.DaysInMonth(time.Year, time.AddMonths(-1).Month)

    previousMonthDates = range(daysInPreviousMonth, daysInPreviousMonth - 7, -1).Select(lambda n: DateTime(time.Year, time.AddMonths(-1).Month, n, 0, 0, 0, DateTimeKind.Utc)).ToList()
    previousMonthDates.AddRange(dates)

    nextMonthDates = range(1, 7).Select(lambda n: DateTime(time.Year, time.Month + 1, n, 0, 0, 0, DateTimeKind.Utc)).ToList()
    previousMonthDates.AddRange(nextMonthDates)

    outp_dates = previousMonthDates
    log(f'{outp_dates}')
    weekStart = outp_dates.Last(lambda d: d.DayOfWeek == DayOfWeek.Monday and d <= time)
    weekEnd = outp_dates.First(lambda d: weekStart < d and d.DayOfWeek == DayOfWeek.Sunday)
    return Week(weekStart, weekEnd)

def _GetMonth(time):
    dates = range(1, DateTime.DaysInMonth(time.Year, time.Month) + 1).Select(lambda n: DateTime(time.Year, time.Month, n, 0, 0, 0, DateTimeKind.Utc)).ToArray()
    return Month(dates.First(), dates.Last())

timeRangeEntityId = Guid.Parse(str(context.ActionParameters['entityId']))
log(f'Time range entity id: {timeRangeEntityId}')

valueFrom = DateTime.Parse(context.ActionParameters['from'].ToString('O'), None, DateTimeStyles.AdjustToUniversal)
log(f'From value: {str(valueFrom)}')

valueTo = DateTime.Parse(context.ActionParameters['to'].ToString('O'), None, DateTimeStyles.AdjustToUniversal)
log(f'To value: {str(valueTo)}')

isSubtract = str(context.ActionParameters['isSubtract'])
if isSubtract == 'TRUE':
    isSubtract = True
else:
    isSubtract = False

timeRangeEntity = find(entitiesQuery(
    locale='fake',
    entitiesByIds=[timeRangeEntityId],
    entitiesByEntityTypeKeys=[TIMERANGE_TYPE],
    entitiesOptions=entitiesOptions(
        includeReferences=True
    ))).SingleOrDefault()
if timeRangeEntity is None:
    raise ValueError(f'Can not find TimeRange entity with id {timeRangeEntityId}')

employeeEntityId = timeRangeEntity.references.Single().Value[0].toEntityId
log(f'Found time range: {timeRangeEntity.id} with employee {employeeEntityId}')

employeeEntity = find(entitiesQuery(
    entitiesByIds=[employeeEntityId],
    entitiesByEntityTypeKeys=[EMPLOYEE_TYPE],
    entitiesOptions=entitiesOptions(
        includeAttributeValuesByAttributeKeys=[TIMEZONE_ATTR]
    )))[0]

try:
    employeesOrgTimezone = int(employeeEntity.attributes[TIMEZONE_ATTR].localizedValues[None].value)
except:
    employeesOrgTimezone = 0

global TODAY
TODAY = valueFrom.AddHours(employeesOrgTimezone).Date
log(f'Employee local date={TODAY}')

week = _GetWeek(TODAY)
log(f'Week: {str(week)}')

month = _GetMonth(TODAY)
log(f'Month: {str(month)}')

entities = find(entitiesQuery(
    locale='fake',
    entitiesByReferencedTo=[referencedToQueryFilter(entityId = employeeEntityId)],
    entitiesByEntityTypeKeys=[DayActivity, WeeklyActivity, MonthlyActivity],
    entitiesOptions=entitiesOptions(
        includeReferences=True,
        includeAttributeValuesByAttributeKeys=['*']
    )))

workAmount = valueTo - valueFrom
if isSubtract == True:
    workAmount = -workAmount
log(f'Work amount: {workAmount}')

def _CheckDayActivity(attributes):
    dayActivityDate = DateTime.Parse(None if attributes[DateAttribute].localizedValues[None].value is None else attributes[DateAttribute].localizedValues[None].value)
    return dayActivityDate == TODAY

def _GetDayActivity(entities):
    log('Try to get daily activity')
    dayActivities = entities.Where(lambda entity: entity.type == DayActivity).ToArray()

    if dayActivities.Length == 0:
        return None

    return next(iter(list(filter(lambda entity: _CheckDayActivity(entity.attributes), dayActivities))), None)

dailyActivity = _GetDayActivity(entities)
if dailyActivity is None:
    log('Daily activity is not found')
else:
    log(f'Daily activity is found {dailyActivity.id}')

def _CheckWeeklyActivity(attributes):
    value = None if attributes[FromAttribute].localizedValues[None].value is None else attributes[FromAttribute].localizedValues[None].value
    weeklyStart = DateTime.Parse(value) >= week.weekStart

    value = None if attributes[ToAttribute].localizedValues[None].value is None else attributes[ToAttribute].localizedValues[None].value
    weeklyEnd = DateTime.Parse(value) <= week.weekEnd

    return weeklyStart and weeklyEnd

def _GetWeeklyActivity(entities):
    log('Try to get weekly activity')
    weeklyActivities = entities.Where(lambda entity: entity.type == WeeklyActivity).ToArray()

    if weeklyActivities.Length == 0:
        return None

    return next(iter(list(filter(lambda entity: _CheckWeeklyActivity(entity.attributes), weeklyActivities))), None)

weeklyActivity = _GetWeeklyActivity(entities)
if weeklyActivity is None:
    log('Weekly activity is not found')
else:
    log(f'Weekly activity is found {weeklyActivity.id}')

def _CheckMonthlyActivity(attributes):
    value = None if attributes[FromAttribute].localizedValues[None].value is None else attributes[FromAttribute].localizedValues[None].value
    monthStart = DateTime.Parse(value) >= month.monthStart

    value = None if attributes[ToAttribute].localizedValues[None].value is None else attributes[ToAttribute].localizedValues[None].value
    monthEnd = DateTime.Parse(value) <= month.monthEnd

    return monthStart and monthEnd

def _GetMonthlyActivity(entities):
    log('Try to get monthly activity')
    monthlyActivities = entities.Where(lambda entity: entity.type == MonthlyActivity).ToArray()
    if monthlyActivities.Length == 0:
        return None

    return next(iter(list(filter(lambda entity: _CheckMonthlyActivity(entity.attributes), monthlyActivities))), None)

monthlyActivity = _GetMonthlyActivity(entities)
if monthlyActivity is None:
    log('Monthly activity is not found')
else:
    log(f'Monthly activity is found {monthlyActivity.id}')

def addOrUpdateAttribute(entity, attributeKey, value, isAdd):
    if isAdd == True:
        entity.addAttribute(attributeKey, None, valueLocale(value=value, display=value))
    elif isAdd == False:
        entity.updateAttribute(attributeKey, None, valueLocale(value=value, display=value))

def addEntityReference(entity, referenceKey, toEntityId):
    entity.addReference(referenceKey, toEntityId)

def format_string(timespan):
    newTs = timespan.ToString("d\.hh\:mm\:ss")
    if TimeSpan.Zero > timespan:
       newTs = '-' + newTs
    return newTs

workAmountValue = format_string(workAmount)
log(f'This timerange workAmount={workAmountValue}')

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
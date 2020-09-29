"""
Calendar module especifically for calendar functions

Last Update: 09/18/2020 - added new filters for events
"""

from moodleapi.request import Request
from moodleapi.settings import professor, week, month
from moodleapi.data.course import Course
from moodleapi.data.export import Export

from datetime import datetime as dt
from re import compile, sub


class Calendar(Request):
    """Calendar Class support montlhy informations only and have
    several functions to filter information and format date."""

    def __init__(self, token):
        self.token = token
        self.allowed_modules = ('assign', 'bigbluebuttonbn')
        self.courses_notallowed = (1, 87177, 5368)

        super().__init__(token)


    def __str__(self):
        return 'Calendar object'


    def _clean(self, value):
         return sub(compile('<.*?>'), '', value)


    def _time(self, epoch):
        from time import ctime

        date = ctime(epoch).split()

        return f'{week[date[0]]}, {date[2]} de {month[date[1]]} às {date[3][:-3]}'


    def _check_time(self, current_h, current_m, assign_h, assign_m, today):
        if current_h > assign_h and today:
            return False
        elif current_h == assign_h and today:
            return False if current_m > assign_m else True
        else:
            return True


    def _verify(self, courseid, instance):
        params = {
            'courseid': courseid,
            'options[0][name]': 'modname',
            'options[0][value]': 'assign',
            'options[1][name]': 'excludecontents',
            'options[1][value]': True,
        }

        return Course(self.token).simple_contents(courseid, instance, params, assign=True)


    def filter(self, value=None, data=None, *args, **kwargs):
        filtering = 'Aula ao vivo - BigBlueButton' if value == 'bbb' else 'Tarefa para entregar via Moodle'

        if value and data:
            filtered = []

            for row in data:
                if row[8] == filtering:
                    filtered.append(row)

            return filtered

        else:
            raise ValueError('Value or data parameter not passed correctly.')


    def monthly(self, y=str(dt.today().year), mon=str(dt.today().month), *args, **kwargs):
        month = Request.get(self, wsfunction='core_calendar_get_calendar_monthly_view', year=y, month=mon)['weeks']

        d, h, m = dt.today().day, dt.today().hour, dt.today().minute


        data = []

        for week in month:
            for day in week['days']:
                for events in day['events']:

                    period = True if d <= int(day['mday']) < d + 15 else False
                    today = True if day['mday'] == d else False

                    deadline = Calendar._clean(self, events['formattedtime'])[:-2] \
                        if events['modulename'] in self.allowed_modules else None

                    up_to_date = Calendar._check_time(self, h, m, int(deadline[:2]), int(deadline[3:5]), today) \
                        if deadline else True


                    if events['modulename'] in self.allowed_modules and events['course']['id'] \
                            not in self.courses_notallowed and period and up_to_date:


                        status, time = None, None
                        if events['modulename'] == 'assign':
                            status, time = Calendar._verify(self, events['course']['id'], events['instance'])


                        data.append([

                            events['course']['fullname'],

                            events['name'].split(' is ')[0] if ' is ' in events['name']
                            else events['name'].split(' está ')[0],

                            Calendar._clean(self, events['description']) if events['description'] != ''
                            else 'Descrição não disponível',

                            'Aula ao vivo - BigBlueButton' if events['modulename'] == 'bigbluebuttonbn' else
                            'Tarefa para entregar via Moodle',

                            day['popovertitle'].split(' eventos')[0],

                            deadline,

                            events['url'],

                            professor[f'{events["course"]["fullname"]}'],

                            f'Tarefa {"não " if status == 0 or not status else ""}entregue',

                            Calendar._time(self, time) if time != 0 and time else ''

                        ])

        return data


    def upcoming(self, check=False, *args, **kwargs):
        events = Request.get(self, wsfunction='core_calendar_get_calendar_upcoming_view')['events']

        try:
            info = args[0]
            filter = kwargs['filter']

        except KeyError:
            filter = None

        data = []

        for event in events:

            if event['course']['id'] not in self.courses_notallowed and event['modulename'] in self.allowed_modules:
                
                deadline = Calendar._clean(self, event['formattedtime'])

                params = {
                    'course': info['course'],
                    'semester': info['semester'],
                    'class': info['class'],
                    'subject': event['course']['fullname'],
                    'guild_id': info['guild_id'],
                } # to professors func

                status, time = None, None
                if event['modulename'] == 'assign' and check:
                    status, time = Calendar._verify(self, event['course']['id'], event['instance'])

                data.append([

                    info['discord_id'], info['guild_id'], info['course'], info['semester'], info['class'],

                    event['course']['fullname'],

                    event['name'].split(' is ')[0] if ' is ' in event['name']
                    else event['name'].split(' está ')[0],

                    Calendar._clean(self, event['description']) if event['description'] != ''
                    else 'Descrição não disponível',

                    'Aula ao vivo - BigBlueButton' if event['modulename'] == 'bigbluebuttonbn' else
                    'Tarefa para entregar via Moodle',
                    
                    deadline[:-7],

                    deadline[-5:],

                    event['url'],

                    professor[f'{event["course"]["fullname"]}'],

                    f'Tarefa {"não " if status == 0 or not status else ""}entregue',

                    Calendar._time(self, time) if time != 0 and time else ''

                ])

        if filter:
            data = Calendar.filter(self, value=filter, data=data)

        return Export(info['db']).to_db(data, check=True if check else False)


    def day(self, y=str(dt.today().year), mon=str(dt.today().month), d=str(dt.today().day), *args, **kwargs):
        events = Request.get(self, wsfunction='core_calendar_get_calendar_day_view', year=y, month=mon, day=d)['events']

        try:
            inf = args[0]
            filter = kwargs['filter']

        except KeyError:
            filter = None

        data = []

        for event in events:

            if event['course']['id'] not in self.courses_notallowed and event['modulename'] in self.allowed_modules:

                deadline = Calendar._clean(self, event['formattedtime'])

                data.append([

                    inf['discord_id'], inf['guild_id'], inf['course'], inf['semester'], inf['class'],

                    event['course']['fullname'],

                    event['name'].split(' is ')[0] if ' is ' in event['name']
                    else event['name'].split(' está ')[0],

                    Calendar._clean(self, event['description']) if event['description'] != ''
                    else 'Descrição não disponível',

                    'Aula ao vivo - BigBlueButton' if event['modulename'] == 'bigbluebuttonbn' else
                    'Tarefa para entregar via Moodle',

                    deadline[:-7],

                    deadline[-5:],

                    event['url'],

                    professor[f'{event["course"]["fullname"]}'],

                ])

        if filter:
            data = Calendar.filter(self, value=filter, data=data)

        return data #Export(kwargs['db']).to_db(data)

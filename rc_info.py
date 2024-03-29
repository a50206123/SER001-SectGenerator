def rebar_info(rebar = '#3') :
    D2no = {
        'D10' : '#3',
        'D13' : '#4',
        'D16' : '#5',
        'D19' : '#6',
        'D22' : '#7',
        'D25' : '#8',
        'D29' : '#9',
        'D32' : '#10',
        'D36' : '#11',
        'D39' : '#12'
    }

    # 規範附錄甲
    rebar_info = {
        '#3': [0.953, 0.7133],
        '#4': [1.27, 1.267],
        '#5': [1.59, 1.986],
        '#6': [1.91, 2.865],
        '#7': [2.22, 3.871],
        '#8': [2.54, 5.067],
        '#9': [2.87, 6.469],
        '#10': [3.22, 8.143],
        '#11': [3.58, 10.07],
        '#12': [3.94, 12.19],
    }

    if rebar[0] == '#' :
        return rebar_info[rebar]
    elif rebar[0] == 'D' :
        return rebar_info[D2no[rebar]]
def ask_url(url, decode_method):
    # 用户代理, 表示告诉服务器我们是什么类型的浏览器
    # 本质上是告诉浏览器, 我们可以接受什么水平的数据
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0"
    }
    req = request.Request(url, headers=head)
    html = None
    try:
        response = request.urlopen(req, timeout=1.5)
        html = response.read().decode(decode_method)
    except error.URLError as e:
        if hasattr(e, 'code'):
            print(e.code)
        elif hasattr(e, 'reason'):
            print(e.reason)
    return html


def get_one_month_daytime(year, month):
    base_url = 'https://richurimo.51240.com/sanya__time__{}_{}__richurimo'.format(year, month)
    html = ask_url(base_url, 'utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    get_times = re.compile(r'>(.*?)</td>')

    result = pd.DataFrame()
    for i, item in enumerate(soup.find_all('tr')):
        if i >= 2:
            item = str(item)
            result.loc[i - 2, '日期'] = datetime.date(year=year, month=month, day=i - 1)
            result.loc[i - 2, '日出时间'] = re.findall(get_times, item)[1]
            result.loc[i - 2, '日中时间'] = re.findall(get_times, item)[2]
            result.loc[i - 2, '日落时间'] = re.findall(get_times, item)[3]
            result.loc[i - 2, '天亮时间'] = re.findall(get_times, item)[5]
            result.loc[i - 2, '天黑时间'] = re.findall(get_times, item)[6]

    return result


def daytime_recording(year_start, year_end):
    writer = pd.ExcelWriter('data/三亚日出日落表.xlsx')
    for year in range(year_start, year_end + 1):
        result = pd.DataFrame()
        for month in range(1, 13):
            temp = get_one_month_daytime(year, month)
            result = pd.concat([result, temp], axis=0)
            time.sleep(random.random() * 5)
        print('year {}  daytime done!'.format(year))
        result.to_excel(writer, sheet_name=str(year), index=False)
    writer.save()

    return None


def get_fest_data(year):
    base_url = 'https://jieqi.supfree.net/cntv.asp?n={}'.format(year)
    html = ask_url(base_url, 'GBK')
    soup = BeautifulSoup(html, 'html.parser')

    get_fest = re.compile(r'">(.*?)</a>')
    get_time = re.compile(r'<td>(.*?)</td>')

    all_tr = soup.find_all('tr')
    fest_list, time_list = [], []
    for tr in all_tr:
        all_td = tr.find_all('td')
        for i, td in enumerate(all_td):
            item = str(td)
            if i % 2 == 0:
                out = re.findall(get_fest, item)[0]
                fest_list.append(out)
            else:
                out = re.findall(get_time, item)[0]
                month = int(out.split(' ')[0].split('月')[0])
                if month == 1:
                    time_list.append('{}年'.format(year + 1) + out)
                else:
                    time_list.append('{}年'.format(year) + out)

    result = []
    for item_list in [fest_list, time_list]:
        result.append(item_list)
    result = pd.DataFrame(result).T
    result.columns = ['节气', '日期时间']

    return result


def fest_recording(year_start, year_end):
    result = pd.DataFrame()
    for year in range(year_start, year_end+1):
        temp = get_fest_data(year)
        result = pd.concat([result, temp], axis=0)
        time.sleep(random.random()*5)
        print('year {}  fest done!'.format(year))

    result.iloc[:, -1] = result.iloc[:, -1].apply(lambda t_str: datetime.datetime.strptime(t_str, '%Y年%m月%d日 %H:%M:%S'))
    result.to_excel('data/节气表.xlsx', index=None)

    return None

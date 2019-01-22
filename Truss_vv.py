from datetime import datetime, timedelta
import pandas as pd
import sys

def change_encoding(data, cols):
    for col in cols:
        try:
            data[col] = data[col].encode('raw_unicode_escape').decode('utf-8')
        except UnicodeDecodeError:
            data[col] = data[col].encode('utf-8')
    return data

def convert_time(row, num_hours):
    new_time = pd.to_datetime(row['Timestamp']) - timedelta(hours=num_hours)
    return new_time.isoformat()

def fix_zip(row, norm_len=5):
    word = str(row.ZIP)
    if len(word) < 5:
        new_zip = word.zfill(norm_len)
        return new_zip
    return str(row.ZIP)

def time_diff(row):
    try:
        foo = datetime.strptime(row['FooDuration'], "%H:%M:%S.%f")
        foo_elements = {'hours': foo.hour, 'minutes': foo.minute, 'seconds': foo.second,
                    'microseconds': foo.microsecond}
        foo_td = timedelta(**foo_elements)
    except ValueError:
        hours, rest = row['FooDuration'].split(':', 1)
        r = datetime.strptime(rest, "%M:%S.%f")
        r_elem = {'hours':  r.hour, 'minutes':  r.minute, 'seconds':  r.second, 'microseconds': r.microsecond}
        foo_td = timedelta(hours=int(hours)) + timedelta(**r_elem)
    try:
        bar = datetime.strptime(row['BarDuration'], "%H:%M:%S.%f")
        bar_elements = {'hours':  bar.hour, 'minutes':  bar.minute, 'seconds':  bar.second,
                        'microseconds': bar.microsecond}
        bar_td = timedelta(**bar_elements)
    except ValueError:
        hours, rest = row['BarDuration'].split(':', 1)
        r = datetime.strptime(rest, "%M:%S.%f")
        r_elem = {'hours':  r.hour, 'minutes':  r.minute, 'seconds':  r.second, 'microseconds': r.microsecond}
        bar_td = timedelta(hours=int(hours)) + timedelta(**r_elem)
#     return str(foo_td + bar_td)
    return (foo_td + bar_td).total_seconds()

def note_fixer(row):
    try:
        return row.encode('utf-8').decode('utf8', 'replace')
    except AttributeError:
        return row.decode('utf8', 'replace').encode('raw_unicode_escape').decode('utf-8', 'replace')

if __name__ == '__main__':
    file = sys.argv[1]
    new_file = sys.argv[2]
    broken_utf8 = pd.read_csv(file, encoding='ISO-8859-1')
    text_cols = ['Address', 'FullName', 'Notes']
    broken_utf8.fillna('', inplace=True)
    broken_utf8[text_cols] = broken_utf8[text_cols].apply(lambda x: change_encoding(x,text_cols), axis=1)
    broken_utf8['Timestamp'] = broken_utf8.apply(lambda x: convert_time(x, 3), axis=1)
    broken_utf8['ZIP'] = broken_utf8.apply(lambda x: fix_zip(x), axis=1)
    broken_utf8['FullName'] = broken_utf8['FullName'].apply(lambda x: x.upper())
    broken_utf8['TotalDuration'] = broken_utf8.apply(lambda x: time_diff(x), axis=1)
    broken_utf8['Notes'] = broken_utf8['Notes'].apply(lambda x: note_fixer(x))
    broken_utf8.to_csv(new_file, index=False)

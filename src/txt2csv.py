import mido
from mido import Message, MidiFile, MidiTrack
import numpy as np
import pandas as pd
import csv
import xlrd
import xlwt
from xlutils.copy import copy
from pathlib import Path
import argparse


# 命令行传递参数
def arguments_transfer():
    # 创建解析器
    parser = argparse.ArgumentParser()
    # 添加位置参数(positional arguments)
    parser.add_argument('txt_path', type=Path, default="vocals.txt",
                        help='读取包含时间和频率的txt路径(default:vocals.txt)')
    # 添加可选参数(-optional arguments)
    parser.add_argument('-bpm', type=float, default=100,
                        help='BPM = Beat Per Minute，歌曲每分钟节拍数(default:100)')
    args = parser.parse_args()
    path = args.txt_path
    Beat_Per_Minute = args.bpm
    return path, Beat_Per_Minute


txt_path, bpm = arguments_transfer()
# 歌曲速度
# bpm = 156

# 1.将txt转为csv
# txt_name = '箱庭の幸福人声.txt'
# filename = re.findall('(?<=_).*?(?=\.)', txt_name)  # 非贪婪匹配'_'和'.'之间的内容
# filename = re.findall('.*?(?=\.txt)', txt_name)
# print(filename[0])
# txt = np.loadtxt("./txt/" + txt_name)
path1 = Path.absolute(txt_path)  # 转成绝对路径
txt = np.loadtxt(txt_path)
txtDF = pd.DataFrame(txt)
Path('/' / path1.parent / "results").mkdir(parents=True, exist_ok=True)
txtDF.to_csv(Path('/') / path1.parent / "results" / (path1.stem + '.csv'), index=False, header=False)

# 2.读取csv的第二列
# with open("./csv/" + str(filename[0]) + '.csv', 'r') as f:
with open(Path('/') / path1.parent / "results" / (path1.stem + '.csv'), 'r') as f:
    reader = csv.reader(f)
    column = [row[1] for row in reader]

# 3.将每个元素与标准值进行比对

standard_name = ['A0', 'A#0', 'B0',
                 'C1', 'C#1', 'D1', 'D#1', 'E1', 'F1', 'F#1', 'G1', 'G#1', 'A1', 'A#1', 'B1',
                 'C2', 'C#2', 'D2', 'D#2', 'E2', 'F2', 'F#2', 'G2', 'G#2', 'A2', 'A#2', 'B2',
                 'C3', 'C#3', 'D3', 'D#3', 'E3', 'F3', 'F#3', 'G3', 'G#3', 'A3', 'A#3', 'B3',
                 'C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4',
                 'C5', 'C#5', 'D5', 'D#5', 'E5', 'F5', 'F#5', 'G5', 'G#5', 'A5', 'A#5', 'B5',
                 'C6', 'C#6', 'D6', 'D#6', 'E6', 'F6', 'F#6', 'G6', 'G#6', 'A6', 'A#6', 'B6',
                 'C7', 'C#7', 'D7', 'D#7', 'E7', 'F7', 'F#7', 'G7', 'G#7', 'A7', 'A#7', 'B7',
                 'C8']

standard_freq = [27.5, 29.135, 30.868,
                 32.703, 34.648, 36.708, 38.891, 41.203, 43.654, 46.249, 48.999, 51.913, 55, 58.27, 61.735,
                 65.406, 69.296, 73.416, 77.782, 82.407, 87.307, 92.499, 97.999, 103.826, 110, 116.541, 123.471,
                 130.813, 138.591, 146.832, 155.563, 164.814, 174.614, 184.997, 195.998, 207.652, 220, 233.082, 246.942,
                 261.626, 277.183, 293.665, 311.127, 329.628, 349.228, 369.994, 391.995, 415.305, 440, 466.164, 493.883,
                 523.251, 554.365, 587.33, 622.254, 659.255, 698.456, 739.989, 783.991, 830.609, 880, 932.328, 987.767,
                 1046.502, 1108.731, 1174.659, 1244.508, 1318.51, 1396.913, 1479.978, 1567.982, 1661.219, 1760,
                 1864.655, 1975.533,
                 2093.005, 2217.461, 2349.318, 2489.016, 2637.02, 2793.826, 2959.955, 3135.963, 3322.438, 3520, 3729.31,
                 3951.066,
                 4186.009]

midi_num = [21, 22, 23,
            24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
            36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
            48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
            60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71,
            72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83,
            84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95,
            96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107,
            108]


# 寻找与number最匹配的音调
def find_stand_name(number):
    if number < 20 or number > 1600:
        return int(0), int(0)
    diffenerce_list = list()
    for i1 in standard_freq:
        diffenerce = i1 - number
        diffenerce_list.append(abs(diffenerce))
    min_difference = min(diffenerce_list)
    number1 = number - min_difference
    number2 = number + min_difference
    if number1 in standard_freq:
        index = standard_freq.index(number1)
    else:
        index = standard_freq.index(number2)
    return standard_name[index], midi_num[index]


# 4.寻找最匹配的音调并存储在数组中
standard_list = list()
midi_list = list()
for i2 in column:
    standard_i, midi_i = find_stand_name(float(i2))
    standard_list.append(standard_i)
    midi_list.append(midi_i)


# print(standard_list)
# print(midi_list)


# 分割函数
def cut(array):
    # 16分音符长度
    min_note_time = 15 / bpm
    time_list = list()
    full_list = list()
    short_list = list()
    freq2 = 0
    count = 0
    begin = 0

    # 构造每一个分组数量的列表
    for i3 in range(len(array) // int(min_note_time * 100) + 1):
        freq1 = min_note_time * 100 * (i3 + 1)
        if (freq1 - int(freq1)) < 0.5:
            freq = int(freq1) - freq2
        else:
            freq = int(freq1) - freq2 + 1
        freq2 = freq2 + freq
        time_list.append(freq)
    # print(time_list)
    # 找到人声部分的开头
    while array[begin] == 0:
        begin += 1
    surplus = len(array) - begin

    # 按分组个数分成二维列表
    while surplus - time_list[count] >= 0:
        part_time = time_list[count]
        for i4 in range(part_time):
            short_list.append(array[i4 + begin])
        full_list.append(short_list)
        begin = begin + part_time
        surplus = surplus - part_time
        count += 1
        short_list = []

    # 把剩下的内容加入二维列表
    if surplus != 0:
        for i in range(surplus):
            short_list.append(array[i + begin])
        full_list.append(short_list)
    return full_list


name_cut_list = cut(standard_list)
midi_cut_list = cut(midi_list)


# print(name_cut_list)
# print(len(name_cut_list))
# print(midi_cut_list)


# 寻找每个小数组中的众数
def find_most(array):
    new_name = list()
    for i in range(len(array)):
        new_number = max(array[i], default='列表为空', key=lambda v: array[i].count(v))
        new_name.append(new_number)
    return new_name


merge_name = find_most(name_cut_list)
merge_midi = find_most(midi_cut_list)


# print(merge_name)
# print(merge_midi)


# 消除重复的音名
def null_less(music_list):
    new_muisc_list = list()
    for i in range(len(music_list) - 1):
        # 1.判断最终位置
        if i == len(music_list) - 2:
            # 1.去除重复
            if music_list[i] == 0:
                if music_list[i + 1] == 0:
                    return new_muisc_list
                else:
                    new_muisc_list.append(music_list[i + 1])
                    return new_muisc_list

            if music_list[i] == music_list[i + 1]:
                new_muisc_list.append(music_list[i])
            else:
                new_muisc_list.append(music_list[i])
                new_muisc_list.append(music_list[i + 1])

        else:
            if music_list[i] == 0:
                continue
            if music_list[i] == music_list[i + 1]:
                continue
            else:
                new_muisc_list.append(music_list[i])
    return new_muisc_list


merge_name = null_less(merge_name)


# print(merge_name)


# 写入Excel表格
def write_xls(new_name, row):
    Path('/' / path1.parent / "results/Excel").mkdir(parents=True, exist_ok=True)
    if Path.is_file(Path('/') / path1.parent / "results/Excel" / (path1.stem + '.xls')):
        old_file = xlrd.open_workbook(Path('/') / path1.parent / "results/Excel" / (path1.stem + '.xls'),
                                      formatting_info=True)
        copy_file = copy(old_file)
        file = copy_file.get_sheet(0)
        for i in range(len(new_name)):
            file.write(i, row, new_name[i])
        copy_file.save(Path('/') / path1.parent / "results/Excel" / (path1.stem + '.xls'))
    else:
        new_file = xlwt.Workbook('encoding = utf-8')
        sheet1 = new_file.add_sheet('sheet1', cell_overwrite_ok=True)
        for i in range(len(new_name)):
            sheet1.write(i, row, new_name[i])
        new_file.save(Path('/') / path1.parent / "results/Excel" / (path1.stem + '.xls'))
    return


# write_xls(merge_name, 0)
# write_xls(merge_midi, 1)

def write_csv(data_list, music_name):
    data_list.insert(0, music_name)
    Path('/' / path1.parent / "results").mkdir(parents=True, exist_ok=True)
    # 新建或追加写入
    with open(Path('/' / path1.parent / "results/database.csv"), mode='a+', newline='', encoding='utf8') as cf:
        wf = csv.writer(cf)
        wf.writerow(data_list)


write_csv(merge_name, path1.stem)
print(path1.stem + ' 已加入数据库')


# 写入midi文件
def write_mid(array):
    # tempo = int((6 * 10 ** 7) / bpm)
    mid = MidiFile()  # 给自己的文件定的.mid后缀
    track = MidiTrack()  # 定义声部，一个MidoTrack()就是一个声部
    mid.tracks.append(track)
    # 默认time=480为全音符即一小节长度
    track.append(Message('program_change', program=41, time=0))
    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0))
    flag = 1
    flag0 = 0
    for i in range(len(array) - 1):
        if array[i] != 0:
            if array[i] == array[i + 1]:
                flag = flag + 1
            else:
                track.append(Message('note_on', note=array[i], velocity=64, time=(120 * flag0)))
                track.append(Message('note_off', note=array[i], velocity=64, time=(120 * flag)))
                flag = 1
                flag0 = 0
        else:
            flag0 = flag0 + 1
    Path('/' / path1.parent / "results/midi").mkdir(parents=True, exist_ok=True)
    mid.save(Path('/') / path1.parent / "results/midi" / (path1.stem + '.mid'))
    return


write_mid(merge_midi)
Path.unlink(Path('/') / path1.parent / "results" / (path1.stem + '.csv'))
print(path1.stem + '.mid' + " 已生成")

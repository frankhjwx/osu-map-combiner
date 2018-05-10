from pydub import AudioSegment
import tkinter as tk
from tkinter import filedialog
import tkinter.messagebox
import os,shutil

configFile = "combiner.config"
osuFolder = "F:\osu!\Songs"
savePath = "CombinerTest/"

class osuFileParser():
    def __init__(self, filenames):
        global Artist, ArtistUnicode, Title, TitleUnicode, Diffname, AR, HP, OD, CS, Mapper, generateAudio
        self.filenames = filenames
        self.fn = []
        self.offset = 0
        self.folderList = []
        self.nameList = []
        self.timingOffset = []
        self.sampleIndex = 0
        self.Title = Title
        self.TitleUnicode = TitleUnicode
        self.Artist = Artist
        self.ArtistUnicode = ArtistUnicode
        self.Diffname = Diffname
        self.AR = AR
        self.CS = CS
        self.OD = OD
        self.HP = HP
        self.Mapper = Mapper
        self.audios = []
        self.start_t = []
        self.end_t = []
        self.generateAudio = generateAudio
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        else:
            shutil.rmtree(savePath)
            os.makedirs(savePath)

    def split(self):
        fn = self.filenames.split('\n')
        fn = fn[0:len(fn)-1]
        folderlist = []
        namelist = []
        for i in range(len(fn)):
            t1, t2 = os.path.split(fn[i])
            folderlist.append(t1)
            namelist.append(t2)
        self.fn = fn
        self.folderList = folderlist
        self.nameList = namelist
        return

    def copyFile(self, srcname, dstname):
        shutil.copy(srcname, dstname)
        return

    def getBaseInfo(self, filename):
        t_start = 100000000
        t_end = -1000
        sec = ""
        file = open(filename, encoding='gb18030', errors='ignore')
        for line in file:
            if 'AudioFilename' in line:
                audioname = line[15:len(line)-1]
            if 'Timing' in line:
                sec = "Timing"
            if 'Colours' in line:
                sec = "Colours"
            if 'HitObjects' in line:
                sec = "HitObjects"
            if sec == "HitObjects" and 'HitObjects' not in line:
                elements = line.split(',')
                t_end = int(elements[2])
                if len(elements)>=6 and elements[5].isdigit():
                    t_end = int(elements[5])
                if t_start > int(elements[2]):
                    t_start = int(elements[2])
        file.close()
        return t_start, t_end, audioname

    def parseSingleFile(self, foldername, filename, offset, start_t, end_t):
        timinglist = []
        objectlist = []
        dic = {}
        sec = ""
        sv = 1
        file = open(filename, encoding='gb18030', errors='ignore')
        lines = file.readlines()
        for line in lines:
            if line == '\n':
                continue
            if 'SliderMultiplier' in line:
                sv = float(line[17:len(line)])
            if 'Timing' in line:
                sec = "Timing"
            if 'Colours' in line:
                sec = "Colours"
            if 'HitObjects' in line:
                sec = "HitObjects"
            if sec == "Timing" and 'Timing' not in line:
                elements = line.split(',')
                if int(float(elements[0])) < start_t:
                    elements[0] = float(elements[0])
                    if elements[6] == "1":
                        dur = float(elements[1]) * 2
                        while elements[0] < start_t:
                            elements[0] += dur
                    else:
                        continue
                    elements[0] = str(elements[0])
                if int(float(elements[0])) > end_t:
                    continue
                elements[0] = str(int(float(elements[0]))+offset)
                if float(elements[1]) < 0:
                    elements[1] = str(float(elements[1])/sv)
                if int(elements[4]) == 0:
                    timinglist.append(','.join(elements))
                elif not elements[4] in dic:
                    self.sampleIndex += 1
                    dic[elements[4]] = self.sampleIndex
                if int(elements[4]) != 0:
                    newIndex = dic[elements[4]]
                    elements[4] = str(newIndex)
                    timinglist.append(','.join(elements))
                if float(elements[1]) > 0 and (lines.index(line) == len(lines) or lines[lines.index(line) + 1].split(',')[0] != line.split(',')[0]):
                    elements[1] = str(-100.0/sv)
                    elements[6] = "0"
                    timinglist.append(','.join(elements))


            if sec == "HitObjects" and 'HitObjects' not in line:
                elements = line.split(',')
                elements[2] = str(int(elements[2]) + offset)
                if len(elements)>=6 and elements[5].isdigit():
                    elements[5] = str(int(elements[5]) + offset)
                objectlist.append(','.join(elements))
        file.close()
        filenamebase = ""
        newname = ""
        print(filename, dic)
        for root, dirs, files in os.walk(foldername):
            for file in files:
                f = os.path.splitext(file)
                if "wav" in f[1] or "ogg" in f[1] or "mp3" in f[1]:
                    if "soft-" in f[0] or "drum-" in f[0] or "normal-" in f[0]:
                        if f[0][len(f[0])-1].isdigit():
                            index = len(f[0])-1
                            while f[0][index].isdigit():
                                index -= 1
                            filenamebase = f[0][0:index+1]
                            if f[0][index+1:len(f[0])] not in dic:
                                continue
                            if dic[f[0][index+1:len(f[0])]] != 1:
                                newname = filenamebase + str(dic[f[0][index+1:len(f[0])]]) + f[1]
                            else:
                                newname = filenamebase + f[1]
                        else:
                            if "1" not in dic:
                                continue
                            filenamebase = f[0]
                            if dic["1"] != 1:
                                newname = filenamebase + str(dic["1"]) + f[1]
                            else:
                                newname = filenamebase + f[1]
                        print(file, newname)
                        self.copyFile(os.path.join(foldername,file), savePath + newname)
        return timinglist, objectlist

    def writeToFile(self, filename, timing, objects):
        f = open(filename, 'w', encoding='gb18030')
        Title = self.Title
        TitleUnicode = self.TitleUnicode
        Artist = self.Artist
        ArtistUnicode = self.ArtistUnicode
        Diffname = self.Diffname
        HP = self.HP
        AR = self.AR
        OD = self.OD
        CS = self.CS
        Mapper = self.Mapper
        f.write('osu file format v14\n'
                '\n'
                '[General]\n'
                'AudioFilename: audio.mp3\n'
                'AudioLeadIn: 0\n'
                'PreviewTime: -1\n'
                'Countdown: 0\n'
                'SampleSet: Soft\n'
                'StackLeniency: 0.7\n'
                'Mode: 2\n'
                'LetterboxInBreaks: 0\n'
                'WidescreenStoryboard: 0\n'
                '\n'
                '[Editor]\n'
                'DistanceSpacing: 1.6\n'
                'BeatDivisor: 4\n'
                'GridSize: 4\n'
                'TimelineZoom: 1\n'
                '\n'
                '[Metadata]\n'
                'Title:'+Title+'\n'
                'TitleUnicode:'+TitleUnicode+'\n'
                'Artist:'+Artist+'\n'
                'ArtistUnicode:'+ArtistUnicode+'\n'
                'Creator:'+Mapper+'\n'
                'Version:'+Diffname+'\n'
                'Source:\n'
                'Tags:\n'
                'BeatmapID:0\n'
                'BeatmapSetID:-1\n'
                '\n'
                '[Difficulty]\n'
                'HPDrainRate:'+HP+'\n'
                'CircleSize:'+CS+'\n'
                'OverallDifficulty:'+OD+'\n'
                'ApproachRate:'+AR+'\n'
                'SliderMultiplier:1\n'
                'SliderTickRate:2\n'
                '\n'
                '[Events]\n'
                '//Background and Video events\n'
                '//Break Periods\n'
                '//Storyboard Layer 0 (Background)\n'
                '//Storyboard Layer 1 (Fail)\n'
                '//Storyboard Layer 2 (Pass)\n'
                '//Storyboard Layer 3 (Foreground)\n'
                '//Storyboard Sound Samples\n\n')
        f.write('[TimingPoints]\n')
        f.write(''.join(timing))
        f.write('\n[HitObjects]\n')
        f.write(''.join(objects))
        f.close()
        return

    def parse(self):
        self.split()
        i = 0
        timing = []
        objects = []
        cut_song_start = []
        cut_song_end = []
        combined_song = 0
        for filename in self.fn:
            t_start, t_end, audioname = self.getBaseInfo(filename)
            self.audios.append(AudioSegment.from_file(self.folderList[i]+'/'+audioname, format="mp3"))
            songLength = len(self.audios[i])
            # cut in time longer than 5s and it's not the first song
            if t_start > 5000 and i > 0:
                cut_song_start.append(t_start - 5000)
            else:
                cut_song_start.append(0)
            # cut out time longer than 5s and it's not the last song
            if songLength - t_end > 5000 and i < len(self.fn) - 1:
                cut_song_end.append(t_end + 5000)
            else:
                cut_song_end.append(songLength)
            print(self.folderList[i], t_start, t_end, songLength, cut_song_start[i], cut_song_end[i])
            if self.generateAudio:
                if combined_song == 0:
                    combined_song = self.audios[i][cut_song_start[i]:cut_song_end[i]].fade_out(min(3000, cut_song_end[i]-t_end))
                else:
                    combined_song = combined_song.append(self.audios[i][cut_song_start[i]:cut_song_end[i]].fade_in(min(3000, t_start))
                                         .fade_out(min(3000, cut_song_end[i]-t_end)), crossfade=0)
                combined_song.export(savePath + "audio.mp3", format="mp3")
            self.timingOffset.append(self.offset - cut_song_start[i])
            self.offset = self.offset + cut_song_end[i] - cut_song_start[i]
            i += 1
        self.start_t = cut_song_start
        self.end_t = cut_song_end
        i = 0
        for filename in self.fn:
            print(self.timingOffset[i])
            tl, obl = self.parseSingleFile(self.folderList[i], filename, self.timingOffset[i], self.start_t[i], self.end_t[i])
            timing.append(''.join(tl))
            objects.append(''.join(obl))
            i += 1
        self.writeToFile(savePath + self.ArtistUnicode+' - '+self.TitleUnicode + ' (' + self.Mapper + ') ['+self.Diffname+'].osu', timing, objects)
        tkinter.messagebox.showinfo('Info', 'The map is combined successfully!')
        print("done")
        return


class WindowCreator():
    def __init__(self):
        self.window = tk.Tk()
        self.s = tk.StringVar()
        self.s.set('')
        self.last = 0

    def button1Callback(self):
        filename = filedialog.askopenfilename(initialdir=osuFolder)
        print(filename)
        self.s.set(self.s.get() + filename + '\n')
        self.last = len(filename)+1
        return

    def button2Callback(self):
        n = len(self.s.get())
        self.s.set(self.s.get()[0:n-self.last])

    def filePathGet(self):
        return self.s.get()

    def run(self):
        parser = osuFileParser(self.s.get())
        parser.parse()

        return

    def create(self):
        window = self.window
        window.title('Map Combiner')
        button1 = tk.Button(window, text="Add a new map", command=self.button1Callback, width=40)\
            .pack(side="top",anchor="w")
        button2 = tk.Button(window, text="Delete the last map", command=self.button2Callback, width=40)\
            .pack(side="top",anchor="w")
        button3 = tk.Button(window, text="Start Making the Map", command=self.run, width=40) \
            .pack(side="top", anchor="w")
        displayText = tk.Label(window, textvariable=self.s, justify='left').pack(fill="y", expand="YES")
        window.mainloop()
        return

def readConfigFile():
    global osuFolder, Artist, ArtistUnicode, Title, TitleUnicode, Diffname, AR, HP, OD, CS, Mapper, savePath, generateAudio
    if not os.path.exists(configFile):
        root = tk.Tk()
        root.withdraw()
        dirname = filedialog.askdirectory(initialdir="C:", title="Please choose your osu! song folder")
        f = open(configFile, "w")
        f.write('generateAudio = true\n'
                'osuPath = ' + dirname + '\n'
                'Artist = Various Artists\n'
                'ArtistUnicode = Various Artists\n'
                'Title = osu!catch Daninintei test Course\n'
                'TitleUnicode = osu!catch Daninintei test Course\n'
                'Diffname = TestRain\n'
                'AR = 9\n'
                'OD = 9\n'
                'CS = 4\n'
                'HP = 10\n'
                'Mapper = Various Creators\n'
                'dstPath = CombinedMap/\n')
        f.close()
        return False
    else:
        file = open(configFile, encoding='gb18030', errors='ignore')
        for line in file:
            if "osuPath =" in line:
                osuFolder = line[line.find("=")+2:len(line)-1]
                print(osuFolder)
            if "Artist =" in line:
                Artist = line[line.find("=")+2:len(line)-1]
            if "ArtistUnicode =" in line:
                ArtistUnicode = line[line.find("=")+2:len(line)-1]
            if "Title =" in line:
                Title = line[line.find("=")+2:len(line)-1]
            if "TitleUnicode =" in line:
                TitleUnicode = line[line.find("=")+2:len(line)-1]
            if "Diffname =" in line:
                Diffname = line[line.find("=")+2:len(line)-1]
            if "AR =" in line:
                AR = line[line.find("=")+2:len(line)-1]
            if "CS =" in line:
                CS = line[line.find("=")+2:len(line)-1]
            if "HP =" in line:
                HP = line[line.find("=")+2:len(line)-1]
            if "OD =" in line:
                OD = line[line.find("=")+2:len(line)-1]
            if "Mapper =" in line:
                Mapper = line[line.find("=")+2:len(line)-1]
            if "dstPath = " in line:
                savePath = line[line.find("=")+2:len(line)-1]
            if "generateAudio" in line:
                if line[line.find("=")+2:len(line)-1] == 'true':
                    generateAudio = True
                elif line[line.find("=")+2:len(line)-1] == 'false':
                    generateAudio = False
                else:
                    raise(RuntimeError('Wrong setting in generateAudio'))
        file.close()
        return True


if not readConfigFile():
    readConfigFile()
w = WindowCreator()
w.create()


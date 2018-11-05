################---------------------------------################
#
# Extensions: A C E F(yyyy from 0000 to 9999, YY from 00 to 99)
#
# Used the pause.
#
# Tips:
# 1. When the word is not in cmudict it print "This word is not included in the cmudict."
#
# 2. When the character(a-z) is not in cmudict it print "This character is not included in the cmudict."
# (which is not possible I think)
#
# 3. Some phone in word like "world" don't have the entire phone and I just pass this.
# (Which sounds ok.)
#
# 4. When the date structure is wrong it print
#  "YYYY should range from 0000 to 9999"
#  "Choose YYYY or YY to type in."
#  "MM should range from 1 to 12"
#  "DD should range from 1 to 31"
#
# 5. if someone types float numbers for the date structure, that won't be recognized as a date structure.
#
# 6. "YY0Y" speaks as "YY o Y"
#
# 7. "YY00" speaks as "YY hundred"
#
# 8. if that day doesn't exist for example 29/02/2001, print "This day doesn't exist."
#
###############---------------------------------#################
import os
import simpleaudio
import argparse
from nltk.corpus import cmudict
import re
import nltk

import numpy as np
#import datetime
#...others?

### NOTE: DO NOT CHANGE ANY OF THE EXISTING ARGUMENTS
parser = argparse.ArgumentParser(
    description='A basic text-to-speech app that synthesises an input phrase using diphone unit selection.')
parser.add_argument('--diphones', default="./diphones", help="Folder containing diphone wavs")
parser.add_argument('--play', '-p', action="store_true", default=False, help="Play the output audio")
parser.add_argument('--outfile', '-o', action="store", dest="outfile", type=str, help="Save the output audio to a file",
                    default=None)
parser.add_argument('phrase', nargs=1, help="The phrase to be synthesised")

# Arguments for extensions
parser.add_argument('--spell', '-s', action="store_true", default=False,
                    help="Spell the phrase instead of pronouncing it")
parser.add_argument('--crossfade', '-c', action="store_true", default=False,
					help="Enable slightly smoother concatenation by cross-fading between diphone units")
parser.add_argument('--volume', '-v', default=None, type=int,
                    help="An int between 0 and 100 representing the desired volume")



args = parser.parse_args()
print(args.diphones)

#---------r1 for filtering cmudict and r2 for filtering file name---------
r1 = re.compile(r'([a-z]+)[0-9]?')
r2 = re.compile(r'([a-z]+_?-_?[a-z]+)')

#---------Check for DD/MM or DD/MM/YY or DD/MM/YYYY---------
# Check how many days in February in that year
# Check if the MM exists in a year
# Check if the DD exists in that month
# Check how to speak YY or YYYY
def check_date_struct(date_string):
    # Settings
    match_date = []
    date_pattern = re.compile(r'(\d+)/(\d+)/?(\d*)')
    match = date_pattern.match(date_string)
    dic_day = {1:'first',2:'second',3:'third',4:'fourth',5:'fifth',
                6:'sixth',7:'seventh',8:'eighth',9:'ninth',10:'tenth',
                11:'eleventh',12:'twelfth',13:'thirteenth',14:'fourteenth',15:'fifteenth',
               16:'sixteenth',17:'seventeenth',18:'eighteenth',19:'nineteenth',20:'twentieth',
               30:'thirtieth','20':'twenty','30':'thirty'}
    list_month=['January','February','March','April','May','June',
                'July','August','September','October','November','December']
    list_day_num = [31,28,31,30,31,30,31,31,30,31,30,31]

    dic_year = {0:'o',1:'one',2:'two',3:'three',4:'four',5:'five',
                6:'six',7:'seven',8:'eight',9:'nine',10:'ten',
                11:'eleven',12:'twelve',13:'thirteen',14:'fourteen',15:'fifteen',
               16:'sixteen',17:'seventeen',18:'eighteen',19:'nineteen',20:'twenty',
               30:'thirty',40:'fourty',50:'fifty',60:'sixty',70:'seventy',80:'eighty',90:'ninety',100:'hundred'}

    if match:
        month = int(match.group(2))
        day = int(match.group(1))
        try:
            year = int(match.group(3))
        except ValueError:
            year = None


        if year != None:
            if year >= 0:
                if year < 100:
                    whole_year = year+1900
                elif year <9999 and year>=1000:
                    whole_year = year
                else:
                    raise ValueError("Choose YYYY or YY to type in.")

                if (whole_year % 4 == 0 and whole_year % 100 != 0) or (whole_year % 400 == 0):
                    list_day_num[1] = 29
            else:
                raise ValueError("YYYY should range from 0000 to 9999")

        # Choose the words
        if month:
            if month<0 or month>12:
                raise ValueError("MM should range from 1 to 12")
            match_month = list_month[month-1]
            match_date.append(match_month)

        if day:
            if day< 1 or day > 31:
                raise ValueError("DD should range from 1 to 31")
            if day > list_day_num[month-1]:
                raise ValueError("This day doesn't exist.")

            if day > 20 and day % 10 !=0:
                (day_1, day_2) = divmod(day, 10)
                match_day_1 = dic_day[str(day_1*10)]
                match_day_2 = dic_day[day_2]
                match_date.append(match_day_1)
                match_date.append(match_day_2)
            else:
                match_day = dic_day[day]
                match_date.append(match_day)

        if year != None:
            (year_1,year_2)=divmod(whole_year,100)
            if year_1>20 and year_1%10 != 0:
                (year_1_1, year_1_2)=divmod(year_1,10)
                match_year_1_1 = dic_year[year_1_1*10]
                match_year_1_2 = dic_year[year_1_2]
                match_date.append(match_year_1_1)
                match_date.append(match_year_1_2)
            else:
                match_year_1 = dic_year[year_1]
                match_date.append(match_year_1)
            if year_2 == 0:
                match_date.append(dic_year[100])
            elif (year_2 > 20 and year_2 % 10 != 0) or year_2<10:
                (year_2_1, year_2_2) = divmod(year_2, 10)
                match_year_2_1 = dic_year[year_2_1*10]
                match_year_2_2 = dic_year[year_2_2]
                match_date.append(match_year_2_1)
                match_date.append(match_year_2_2)
            else:
                match_year_2 = dic_year[year_2]
                match_date.append(match_year_2)

        return match_date
    return None



class Synth:
    def __init__(self, wav_folder):
        self.diphones = {}
        self.sound = simpleaudio.Audio()
        self.get_wavs(wav_folder)

    # get all the sound data we need to make speak a word.
    def get_wavs(self, wav_folder):
        for root, dirs, files in os.walk(wav_folder, topdown=False):
            for file in files:
                name = nltk.tokenize.regexp_tokenize(file,r2)
                try:
                    self.sound.load(wav_folder+'/'+file)
                except FileNotFoundError:
                    print("Cannot find the wav files:{0}.".format(wav_folder+'/'+file))
                self.diphones[name[0]] = self.sound.data
        if self.diphones =={}:
            raise ValueError("You sure to put the right directory for diphone?")



class Utterance:
    def __init__(self, phrase):
        print(phrase)
        self.phrase =phrase
        self.tokens = []
        # self.wav = []

    def regexp_tokenize_word(self):
        pattern = r'\W*([a-z]+[-]?[a-z]+)\W*'
        self.tokens.extend(nltk.tokenize.regexp_tokenize(self.phrase.lower(), pattern))
        # print(self.tokens)

    def regexp_tokenize_char(self):
        pattern = r'([a-z])'
        self.tokens.extend(nltk.tokenize.regexp_tokenize(self.phrase.lower(), pattern))
        # print(self.tokens)

    def list2str(self,origin_list):
        list_phone_element =[]
        str_list = []
        for i in range(len(origin_list)):
            origin_list[i] = nltk.regexp_tokenize(origin_list[i].lower(),r1)
            list_phone_element.extend(origin_list[i]*2)
        return list_phone_element

    # Get the spelling order
    def get_phone_spellseq(self):
        self.regexp_tokenize_char()
        phone_list = []
        list_phone_element =[]
        for i in self.tokens:
            try:
                list_cmudic = cmudict.dict()[i][0]
            except KeyError:
                print("This character '{0}' is not included in the cmudict.".format(i))
                return None
            list_phone_element.extend(self.list2str(list_cmudic))
        # print(list_phone_element)
        list_phone_element.insert(0,"pau")
        list_phone_element.append("pau")

        list2 = np.reshape(list_phone_element,(int(len(list_phone_element)/2),2))
        for i in list2:
            phone_list.append(i[0]+'-'+i[1])
        # print(phone_list)
        return phone_list

    # Get the words order
    def get_phone_seq(self):
        list_phone_element =[]
        self.tokens.extend(nltk.word_tokenize(self.phrase))
        tokens_date = self.tokens[:]
        # Add the date
        for i in range(len(self.tokens)):
            match_date = check_date_struct(self.tokens[i])
            if match_date:
                insert_date = match_date[::-1]
                for j in insert_date:
                    tokens_date.insert(i,j)
        self.tokens = tokens_date
        tokens_2 = self.tokens[:]

        # Remove the non-word part
        for i in self.tokens:
            word_pattern = re.compile(r'([A-Za-z]+)')
            word_capture = word_pattern.match(i)
            if not word_capture:
                tokens_2.pop(tokens_2.index(i))
        self.tokens = tokens_2
        phone_list = []

        # Form the seq
        for i in self.tokens:
            try:
                list_cmudic = cmudict.dict()[i.lower()][0]
            except KeyError:
                print("This word '{0}' is not included in the cmudict.".format(i))
                return None
            # phone_list.extend(self.list2str(list_cmudic))
            list_phone_element.extend(self.list2str(list_cmudic))
        # print(list_phone_element)
        list_phone_element.insert(0,"pau")
        list_phone_element.append("pau")
        list2 = np.reshape(list_phone_element,(int(len(list_phone_element)/2),2))
        for i in list2:
            phone_list.append(i[0]+'-'+i[1])
        # print(phone_list)
        return phone_list


#---------------soomth the diphone----------------
def get_smooth(phone_data_list):
    num = int(out.rate * 0.01)
    fade_1 = np.arange(0, 1, 1 / num)
    fade_2 = fade_1[::-1]
    length = 0
    for phone_data in phone_data_list:
        phone_data[:num] = np.multiply(phone_data[:num], fade_1)
        phone_data[len(phone_data) - num:] = np.multiply(phone_data[len(phone_data) - num:], fade_2)
        length += len(phone_data)


    length = length-(len(phone_data_list)-1)*num
    repeat = len(phone_data_list)-1
    array = np.zeros(length)
    
    # ocerlap and cross fading here
    start = 0
    for i in range(0, repeat + 1):
        end = start + len(phone_data_list[i])
        phone_data = phone_data_list[i]
        array[start:end] = array[start:end] + phone_data
        start = end - num
    array = np.rint(array).astype(np.int16)
    return array







if __name__ == "__main__":

    utt = Utterance(args.phrase[0])
    # spell or not
    if args.spell:
        phone_seq = utt.get_phone_spellseq()
    else:
        phone_seq = utt.get_phone_seq()

    # if all the words can be found in cmudict we start to synth them.
    if phone_seq:
        # print(phone_seq)
        diphone_synth = Synth(wav_folder=args.diphones)
        diphone_synth.get_wavs(wav_folder=args.diphones)

        out = simpleaudio.Audio(rate=16000)

        phone_data_list = []


        for i in phone_seq:
            try:
                phone_data = diphone_synth.diphones[i]
            # Combinations of sounds which are not included in the wav files provided will be ignored. For example: hh_hh
            except KeyError:
                pass

            phone_data_list.append(phone_data)

        if args.crossfade:
            out.data = np.array(get_smooth(phone_data_list))
        else:
            for phone_data in phone_data_list:
                out.data = np.append(out.data, phone_data)


        if args.volume:
            if not (args.volume>= 0 and args.volume<=100):
                raise ValueError("The volume is from 0 to 100.")

            # Do not need this since we limit the type in parse.add_argument()
            # if not isinstance(args.volume,int):
            #     raise TypeError("The volume should be a int.")
            out.rescale(args.volume/100.0)

        if args.play:
            out.play()

        if args.outfile:
            out.save(args.outfile)

        print(out.data, type(out.data))






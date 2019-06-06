import subprocess
import argparse
import re
from datetime import datetime as dt
import os


argumentsDescMsg = 'Initialize bot options.'
inputArgHelp     = 'input audio file'
outputDirArgHelp = 'output directory'
intervalsArgHelp = 'list of intervals of the form: hh:mm:ss(start) hh:mm:ss(end)'
funcDefault      = 'split_by_intervals'
timeRegex        = '(\d{2})(:(\d{2})){2}$' #it stands for hh:mm:ss
notClosedIntvErr = 'Some interval is not closed'
greaterStartErr  = 'Interval with greater start: '
greaterThnDurErr = 'Interval greater than total duration: '
dirError         = '{0} is not a directory or does not exist'


def get_audio_duration(input_file):
    durationCall = 'ffmpeg -i Zapada_2019.03.02.wav 2>&1 | grep Duration'
    duration = subprocess.check_output(durationCall, shell=True)
    return str(duration)[14:22]


def split_interval(input_file, output_file, start, end):
    split = 'ffmpeg -i {ifl} -ss {st} -vn -c copy -to {ed} {of}'.format(
            ifl=input_file, of=output_file, st=start, ed=end)
    subprocess.call(split, shell=True)


def get_output_file(inputFile, outputDir, start, end):
    return outputDir+inputFile[0:-4]+'_'+start+'-'+end+inputFile[-4::1]


def split_by_intervals(inputFile, outputDir, intervals):
    for interval in intervals:
        outputFile = get_output_file(inputFile, outputDir, interval['start'], interval['end'])
        split_interval(inputFile, outputFile, interval['start'], interval['end'])


def dir_path_type(dirname):
    if not os.path.exists(dirname):
        msg = dirError.format(dirname)
        raise argparse.ArgumentTypeError(msg)
    else:
        return dirname


def time_regex_type(s, pat=re.compile(timeRegex)):
    if not pat.match(s):
        raise argparse.ArgumentTypeError()
    return s


def normalize_intervals(agrIntervals, maxEnd):
    if len(agrIntervals) % 2 != 0:
        raise ValueError(notClosedError)

    intervals = [{'start':interval[0], 'end':interval[1]} for interval in 
            zip(agrIntervals[0::2], agrIntervals[1::2])]
    
    HMS = '%H:%M:%S'
    for interval in intervals:
        if dt.strptime(interval['end'], HMS) > dt.strptime(maxEnd, HMS):
            raise ValueError(greaterThnDurErr+interval['start']+' '+interval['end'])
        if dt.strptime(interval['start'], HMS) > dt.strptime(interval['end'], HMS):
            raise ValueError(greaterStartErr+interval['start']+' '+interval['end'])

    return intervals


def parse_input():
    parser = argparse.ArgumentParser(description=argumentsDescMsg, 
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('inputfile', metavar='INPUT_FILE', type=dir_path_type, help=inputArgHelp)
    parser.add_argument('outputdir', metavar='OUTPUT_DIRECTORY', type=dir_path_type, help=outputDirArgHelp)
    parser.add_argument('intervals', metavar='INTERVALS', type=time_regex_type, nargs='+', help=intervalsArgHelp)
    arguments = parser.parse_args()

    arguments.intervals = normalize_intervals(arguments.intervals, get_audio_duration(arguments.inputfile))
    return arguments


def main():
    arguments = parse_input()
    split_by_intervals(arguments.inputfile, arguments.outputdir, arguments.intervals)


if __name__ == '__main__':
    main()

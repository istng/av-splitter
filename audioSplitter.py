import subprocess
import argparse
import re
from datetime import datetime as dt
import os


inputArgHelp     = 'input audio file'
outputDirArgHelp = 'output directory'
intervalsArgHelp = 'list of intervals with shape: hh:mm:ss hh:mm:ss [name]'
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


def get_output_file(inputFile, outputDir, interval):
    if 'name' in interval:
        return outputDir+interval['name']+inputFile[-4::1]
    return outputDir+inputFile[0:-4]+'_'+interval['start']+'-'+interval['end']+inputFile[-4::1]


def split_by_intervals(inputFile, outputDir, intervals):
    for interval in intervals:
        outputFile = get_output_file(inputFile, outputDir, interval)
        split_interval(inputFile, outputFile, interval['start'], interval['end'])


def dir_path_type(dirname):
    if not os.path.exists(dirname):
        msg = dirError.format(dirname)
        raise argparse.ArgumentTypeError(msg)
    else:
        return dirname


def validate_time_format(s, pat=re.compile(timeRegex)):
    if not pat.match(s):
        raise ValueError('Invalid time format on: '+s)


def check_intervals_correctness(intervals, maxEnd):
    HMS = '%H:%M:%S'
    for interval in intervals:
        if dt.strptime(interval['end'], HMS) > dt.strptime(maxEnd, HMS):
            raise ValueError(greaterThnDurErr+interval['start']+' '+interval['end'])
        if dt.strptime(interval['start'], HMS) > dt.strptime(interval['end'], HMS):
            raise ValueError(greaterStartErr+interval['start']+' '+interval['end'])


def normalize_intervals(argIntervals):
    intervals = []
    for argInterval in argIntervals:
        interval = {'start': argInterval[0], 'end': argInterval[1]}
        if len(argInterval) == 3:
            interval['name'] = argInterval[2]
        intervals.append(interval)
    return intervals


class IntervalAndName(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        if not (2 <= len(values) <= 3):
            raise argparse.ArgumentError(self, "%s takes 2 or 3 values, %d given" % (option_string, len(values)))
        else:
            validate_time_format(values[0])
            validate_time_format(values[1])
        super(IntervalAndName, self).__call__(parser, namespace, values, option_string)


def parse_input():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    req_flags_grp = parser.add_argument_group(title='Required with flags')
    parser.add_argument('inputfile', metavar='INPUT_FILE', type=dir_path_type, help=inputArgHelp)
    parser.add_argument('outputdir', metavar='OUTPUT_DIRECTORY', type=dir_path_type, help=outputDirArgHelp)
    req_flags_grp.add_argument('--intervals', '-i', metavar='INTERVALS', type=str, nargs='+', action=IntervalAndName, help=intervalsArgHelp)
    arguments = parser.parse_args()

    arguments.intervals = normalize_intervals(arguments.intervals)
    check_intervals_correctness(arguments.intervals, get_audio_duration(arguments.inputfile))
    return arguments


def main():
    arguments = parse_input()
    split_by_intervals(arguments.inputfile, arguments.outputdir, arguments.intervals)


if __name__ == '__main__':
    main()

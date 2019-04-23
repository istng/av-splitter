import subprocess
import argparse
from collections import namedtuple


argumentsDescMsg = 'Initialize bot optios.'
functionArgHelp  = 'function to use'
inputArgHelp     = 'input audio file'
outputDirArgHelp    = 'output directory'
intervalsArgHelp = 'list of intervals of the form: hh:mm:ss(start) hh:mm:ss(end)'
funcDefault      = 'split_by_intervals'

Interval  = namedtuple('Interval', ['start', 'end'])
AudioLine = namedtuple('AudioLine', ['audio', 'outputDir', 'intervals'])

def split_by_intervals(input_file, output_file, start, end):
    cut_command = 'ffmpeg -i {ifl} -ss {st} -vn -c copy -to {ed} {of}'.format(
            ifl=input_file, of=output_file, st=start, ed=end)
    subprocess.call(cut_command, shell=True)


def parse_input():
    parser = argparse.ArgumentParser(description=argumentsDescMsg, 
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    #TODO: support for more functions
    #parser.add_argument('-f', metavar='FUNCTION', type=str, default=funcDefault, help=functionArgHelp)
    parser.add_argument('input', metavar='INPUT FAILE', type=str, help=inputArgHelp)
    parser.add_argument('outputdir', metavar='OUTPUT FILE', type=str, help=outputDirArgHelp)
    parser.add_argument('intervals', metavar='INTERVALS', type=str, nargs='+', help=intervalsArgHelp)
    args = parser.parse_args()
 
    intervals = [Interval(start=interval[0], end=interval[1]) for interval in 
            zip(args.intervals[0::2], args.intervals[1::2])]
    return AudioLine(audio=args.input, outputDir=args.outputdir, intervals=intervals)


def main():
    audioLine = parse_input()
    for interval in audioLine.intervals:
        split_by_intervals(audioLine.audio, audioLine.outputDir, interval.start, interval.end)


if __name__ == '__main__':
    main()

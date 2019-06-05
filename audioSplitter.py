import subprocess
import argparse


argumentsDescMsg = 'Initialize bot options.'
inputArgHelp     = 'input audio file'
outputDirArgHelp = 'output directory'
intervalsArgHelp = 'list of intervals of the form: hh:mm:ss(start) hh:mm:ss(end)'
funcDefault      = 'split_by_intervals'


def split_interval(input_file, output_file, start, end):
    split = 'ffmpeg -i {ifl} -ss {st} -vn -c copy -to {ed} {of}'.format(
            ifl=input_file, of=output_file, st=start, ed=end)
    subprocess.call(split, shell=True)


def get_output_file(inputFile, outputDir, start, end):
    return outputDir+'_'+start+'-'+end+inputFile[-4::1]


def split_by_intervals(inputFile, outputDir, intervals):
    for interval in intervals:
        outputFile = get_output_file(inputFile, outputDir, interval['start'], interval['end'])
        split_interval(inputFile, outputFile, interval['start'], interval['end'])


def normalize_arguments(arguments):
    intervals = [{'start':interval[0], 'end':interval[1]} for interval in 
            zip(arguments.intervals[0::2], arguments.intervals[1::2])]
    return {'audio':arguments.input, 'outputDir':arguments.outputdir, 'intervals':intervals}


def parse_input():
    parser = argparse.ArgumentParser(description=argumentsDescMsg, 
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('input', metavar='INPUT_FILE', type=str, help=inputArgHelp)
    parser.add_argument('outputdir', metavar='OUTPUT_DIRECTORY', type=str, help=outputDirArgHelp)
    parser.add_argument('intervals', metavar='INTERVALS', type=str, nargs='+', help=intervalsArgHelp)
    arguments = parser.parse_args()
 
    return normalize_arguments(arguments)


def main():
    audioLine = parse_input()
    split_by_intervals(audioLine['audio'], audioLine['outputDir'], audioLine['intervals'])


if __name__ == '__main__':
    main()

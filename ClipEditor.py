#!/usr/bin/env python
"""
ClipEditor.py: Create video clips from a source video using information from a .csv formatted input file.
"""

__author__ = "Jeremy Whitcher"
__contact__ = "jwwhitch@gmail.cm"
__license__ = "MIT License"
__date__ = "2023-12-30"
__version__ = "1.0.0"
__status__ = "Production"

import os
import csv
import yaml
import moviepy.editor as mpy
import logging
from logging.handlers import RotatingFileHandler


def init_logger(log_filename):
    """
    Initializes a logger that writes to both the console and a rotating log file.

    :param log_filename: The name of the log file.
    :type log_filename: str
    :return: A logger object.
    :rtype: logging.Logger
    """
    logger = logging.getLogger(log_filename)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    file_handler = RotatingFileHandler(f"{log_filename}.log", backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


logger = init_logger("ClipEditor")


class VideoEditor:
    """
    A class that allows editing video clips using moviepy.

    :param video_name: The name of the video file to edit.
    :type video_name: str
    :param settings: A dictionary of settings for the video editing, such as threads, fps, codec, etc.
    :type settings: dict
    """

    def __init__(self, video_name, settings):
        self.video = mpy.VideoFileClip(video_name)
        self.settings = settings

    @staticmethod
    def _convert_to_hms(time_str):
        """
        Converts a time string in the format of mm:ss to hh:mm:ss.

        :param time_str: The time string to convert.
        :type time_str: str
        :return: The converted time string in hh:mm:ss format.
        :rtype: str
        """
        logger.debug(f'Time conversion for {time_str}')
        minutes, seconds = map(int, time_str.split(':'))
        hours = minutes // 60
        minutes %= 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def close_source(self):
        """
        Closes the source video file.
        """
        self.video.close()

    def create_clip(self, start_time, end_time, output_file):
        """
        Creates a video clip from the source video file using the given start and end times.

        :param start_time: The start time of the clip in mm:ss format.
        :type start_time: str
        :param end_time: The end time of the clip in mm:ss format.
        :type end_time: str
        :param output_file: The name of the output file without extension.
        :type output_file: str
        """
        clip_start = VideoEditor._convert_to_hms(start_time)
        clip_end = VideoEditor._convert_to_hms(end_time)
        clip_name = f"{output_file}_{clip_start.replace(':', '')}-{clip_end.replace(':', '')}.mp4"
        if os.path.exists(clip_name):
            logger.info(f'Skipping {clip_name}, a file already exists.')
            return
        clip = self.video.subclip(clip_start, clip_end)
        os.makedirs(os.path.dirname(clip_name), exist_ok=True)
        clip.write_videofile(
            os.path.abspath(clip_name),
            threads=self.settings['threads'],
            fps=self.settings['fps'],
            codec=self.settings['vcodec'],
            preset=self.settings['compression'],
            ffmpeg_params=["-crf", str(self.settings['fps'])])


class VideoClipCSVReader:
    """
    A class that reads a CSV file containing information about video clips.

    :param filename: The name of the CSV file to read.
    :type filename: str
    """

    def __init__(self, filename):
        self.filename = filename

    @staticmethod
    def _generate_clip_name(row):
        """
        Generates a clip name based on the row data.

        :param row: A dictionary containing the row data, such as From, To, Name, Play, Game, File.
        :type row: dict
        :return: The generated clip name in the format of base_file-Name-Play.
        :rtype: str
        """
        # From, To, Name, Play, Game, File
        base_file = os.path.basename(os.path.splitext(row['File'])[0]).replace('(', '').replace(')', '')
        path = f"{base_file}-{row['Name']}".replace(' ', '_')
        name = f"{base_file}-{row['Name']}-{row['Play']}".replace(' ', '_')
        return os.path.join(path, name)

    def clip_list(self):
        """
        Returns a generator that yields the clip information from the CSV file.

        :return: A generator that yields a dictionary for each clip, with the keys being the column names and the values being the corresponding data. The dictionary also contains a 'Clip Name' key that holds the generated clip name.
        :rtype: generator
        """
        with open(self.filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                row['Clip Name'] = VideoClipCSVReader._generate_clip_name(row)
                yield row


def edit_video(settings):
    """
    Edits a video file according to the settings and the clip information.

    :param settings: A dictionary of settings for the video editing, such as threads, fps, codec, etc.
    :type settings: dict
    """
    clips = VideoClipCSVReader(settings['clip_file'])
    prev_source = None
    editor = None
    for clip in clips.clip_list():
        source = clip['File']
        name = clip['Clip Name'].strip()
        start_time = clip['From'].strip()
        end_time = clip['To'].strip()
        logger.info(f"Processing {source} {start_time}-{end_time}")
        if clip['File'] and prev_source != source:
            logger.debug(f"Creating a new class for {source}")
            prev_source = source
            if editor:
                editor.close_source()
            editor = VideoEditor(source, settings)
        editor.create_clip(start_time, end_time, name)
    if editor:
        editor.close_source()


def main():
    with open('settings.yaml') as yaml_stream:
        settings = yaml.load(yaml_stream, Loader=yaml.Loader)
    edit_video(settings)
    return 0


if __name__ == '__main__':
    exit(main())

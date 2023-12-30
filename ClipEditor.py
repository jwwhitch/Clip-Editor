import os
import csv
import yaml
import moviepy.editor as mpy
import logging
from logging.handlers import RotatingFileHandler


def init_logger(log_filename):
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
    def __init__(self, video_name, settings):
        self.video = mpy.VideoFileClip(video_name)
        self.settings = settings

    @staticmethod
    def _convert_to_hms(time_str):
        logger.debug(f'time conversion for {time_str}')
        minutes, seconds = map(int, time_str.split(':'))
        hours = minutes // 60
        minutes %= 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def create_clip(self, start_time, end_time, output_file):
        clip_start = VideoEditor._convert_to_hms(start_time)
        clip_end = VideoEditor._convert_to_hms(end_time)
        clip_name = f"{output_file}_{clip_start.replace(':', '')}-{clip_end.replace(':', '')}.mp4"
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
    def __init__(self, filename):
        self.filename = filename

    @staticmethod
    def _generate_clip_name(row):
        # From, To, Name, Play, Game, File
        base_file = os.path.basename(os.path.splitext(row['File'])[0])
        path = f"{base_file}-{row['Name']}".replace(' ','_')
        name = f"{base_file}-{row['Name']}-{row['Play']}".replace(' ', '_')
        return os.path.join(path, name)

    def clip_list(self):
        with open(self.filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                row['Clip Name'] = VideoClipCSVReader._generate_clip_name(row)
                yield row


def edit_video(settings):
    clips = VideoClipCSVReader(settings['clip_file'])
    prev_source = None
    editor = None
    for clip in clips.clip_list():
        source = clip['File']
        name = clip['Clip Name']
        start_time = clip['From'].strip()
        end_time = clip['To'].strip()
        logger.info(f"processing {source} {start_time}-{end_time}")
        if clip['File'] and prev_source != source:
            logger.debug(f"creating a new class for {source}")
            prev_source = source
            editor = VideoEditor(source, settings)
        editor.create_clip(start_time, end_time, name)


def main():
    with open('settings.yaml') as yaml_stream:
        settings = yaml.load(yaml_stream, Loader=yaml.Loader)
    edit_video(settings)
    return 0


if __name__ == '__main__':
    exit(main())

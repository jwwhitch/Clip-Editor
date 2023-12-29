import os
import yaml
import moviepy.editor as mpy


def convert_time(time_str):
    seconds = time_str[-2:]
    minutes = time_str[-4:-2]
    hours = time_str[:-4]
    if not hours:
        hours = '00'
    return f'{hours}:{minutes}:{seconds}'


def convert_time_str(time_str):
    hours, minutes, seconds = time_str.split(':')
    return (int(hours) * 3600.0) + (int(minutes) * 60.0) + float(seconds)


def edit_video(settings):
    video = mpy.VideoFileClip(settings['load_title'])
    cuts = []
    for raw_time in settings['raw_times']:
        time_str = convert_time(raw_time)
        time_sec = convert_time_str(time_str)
        cuts.append((time_sec - settings['clip_time'] / 2.0, time_sec + settings['clip_time'] / 2.0))
    os.makedirs(settings['save_path'], exist_ok=True)
    for number, cut in enumerate(cuts, 1):
        clip = video.subclip(cut[0], cut[1])
        out_title = os.path.join(
            settings['save_path'],
            os.path.basename(f"{os.path.splitext(settings['save_title'])[0]}-"
                             f"{number}{os.path.splitext(settings['save_title'])[1]}"))
        clip.write_videofile(
            out_title,
            threads=settings['threads'],
            fps=settings['fps'],
            codec=settings['vcodec'],
            preset=settings['compression'],
            ffmpeg_params=["-crf", str(settings['fps'])])
    video.close()


def main():
    with open('settings.yaml') as yaml_stream:
        settings = yaml.load(yaml_stream, Loader=yaml.Loader)
    edit_video(settings)
    return 0


if __name__ == '__main__':
    exit(main())

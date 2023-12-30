# Video Clip Editor

This Python script is used to create video clips from a source video based on time ranges specified in a CSV file. The script also logs its operations to both the console and a rotating log file.

## Dependencies

The script depends on the following Python libraries:
- os
- csv
- yaml
- moviepy.editor
- logging
- logging.handlers.RotatingFileHandler

## Classes and Functions

The script contains the following classes and functions:

- `init_logger(log_filename)`: Initializes a logger that writes to both the console and a rotating log file.

- `VideoEditor`: A class that represents a video editor. It has the following methods:
  - `__init__(self, video_name, settings)`: Initializes a new instance of the `VideoEditor` class.
  - `_convert_to_hms(time_str)`: Converts a time string in the format "minutes:seconds" to "hours:minutes:seconds".
  - `create_clip(self, start_time, end_time, output_file)`: Creates a clip from the video for the specified time range and writes it to the specified output file.

- `VideoClipCSVReader`: A class that reads a CSV file and yields one row per call with an additional field `Clip Name`. It has the following methods:
  - `__init__(self, filename)`: Initializes a new instance of the `VideoClipCSVReader` class.
  - `_generate_clip_name(row)`: Generates a clip name based on the fields in the row.
  - `clip_list(self)`: Yields one row per call from the CSV file.

- `edit_video(settings)`: Edits a video based on the settings provided.

- `main()`: The main function of the script. It loads the settings from a YAML file and calls the `edit_video` function with these settings.

## Usage

To run the script, you need to have a settings.yaml file in the same directory. The settings.yaml file should contain the necessary settings for the video editing operation.

You can run the script using the following command:

```shell
python script_name.py

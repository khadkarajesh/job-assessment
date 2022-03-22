import re
from pathlib import Path
from typing import List

from country_top_song import LOG_FORMAT_REGEX
from logger import logger
from utils import sort_by_value

OUTPUT_FILE_NAME_PREFIX = "user_top50_"


class UserTopSong:
    def __init__(self, n: int,
                 data_path: Path,
                 output_path: Path,
                 input_file):
        self.n = n
        self.data_path = data_path
        self.output_path = output_path
        self.input_file = input_file
        self.user_songs = {}

    def count_frequency_of_songs_by_user(self, file):
        for line in file:
            pattern = re.compile(LOG_FORMAT_REGEX)
            if pattern.match(line):
                results = line.strip().split("|")
                user_id = results[1]
                song_id = results[0]
                if self.user_songs.get(user_id):
                    song_dict = self.user_songs[user_id]
                    if song_dict.get(song_id):
                        song_dict[song_id] += 1
                    else:
                        song_dict[song_id] = 1
                else:
                    self.user_songs[user_id] = {song_id: 1}

    def filter_top_n_songs(self, count_dict: dict) -> List[str]:
        result = []
        for key in count_dict.keys():
            songs_dict = count_dict.get(key)
            sorted_songs_dict = sort_by_value(songs_dict)
            song_txt = ""
            top_songs_keys = list(sorted_songs_dict.keys())[0:self.n]
            for song in top_songs_keys:
                song_txt = song_txt + f"{song}:{sorted_songs_dict[song]},"
            result.append(f"{key}|{song_txt.rstrip(',')}\n")
        return result

    def get_filename(self) -> str:
        log_file_date = self.input_file[7:17]
        return f"{OUTPUT_FILE_NAME_PREFIX}{log_file_date}.txt"

    def discover(self):
        try:
            with open(self.data_path / 'input' / self.input_file) as f:
                self.count_frequency_of_songs_by_user(f)
                top_n_songs = self.filter_top_n_songs(count_dict=self.user_songs)
                self.save(top_n_songs)
        except FileNotFoundError as e:
            logger.error(e)

    def save(self, values: List[str]) -> None:
        with open(self.output_path / self.get_filename(), "w") as result_file:
            result_file.writelines(values)

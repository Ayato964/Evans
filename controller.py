import json
import os
from pathlib import Path
import pygame

class MusicList:
    def __init__(self):
        self._musics = self._init_music_list()
        self.music_idx = 0

    def _init_music_list(self):
        music_list = list()
        target_dir = Path("./resource/musics/")
        json_files = list(target_dir.rglob('*.json'))
        for path in json_files:
            with open(path, 'r', encoding='utf-8') as f:
                data: dict = json.load(f)
                data["root"] = os.path.dirname(path)
                music_list.append(data)
        return music_list

    def __len__(self):
        return len(self._musics)

    def get_idx(self):
        return self.music_idx

    def play(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            print(os.path.join(self._musics[self.music_idx]["root"],
                                                 self._musics[self.music_idx]["media"]["music"] + ".midi"))
            pygame.mixer.music.load(os.path.join(self._musics[self.music_idx]["root"],
                                                 self._musics[self.music_idx]["media"]["music"] + ".midi"))
            pygame.mixer.music.play()
        except pygame.error as e:
            print(f"再生できない！！！！     {e}")

    def stop(self):
        pygame.mixer.music.stop()

    def set_next(self):
        if self.music_idx + 1 < len(self._musics):
            self.music_idx += 1
        else:
            self.music_idx = 0

    def set_back(self):
        if self.music_idx - 1 >= 0:
            self.music_idx -= 1
        else:
            self.music_idx = len(self._musics) - 1

    def __getitem__(self, item):
        return self._musics[item]

import re
from ooo import FileInfo


def get_category(name):
    tv = re.compile(".*S[0-9][0-9].*|.*complete.*|.*\\.E[0-9].*", re.IGNORECASE)
    if tv.match(name):
        return "tv"
    return "movie"


assert get_category("Game of Thrones S01E07 HDTV XviD-ASAP") == "tv"
assert get_category("Game of Thrones S01 HDTV XviD-ASAP") == "tv"
assert get_category("Game of Thrones E1 completed") == "tv"
assert get_category("Game of Thrones.E1") == "tv"
assert get_category("Game of Throne1") == "movie"
assert get_category("FearOfTheDragon") == "movie"


assert FileInfo.normalize_name("123456789.avi") == "123456789.avi"
assert FileInfo.normalize_name("abcdefghijklmnopqrstuvwxyz") == "abcdefghijklmnopqrstuvwxyz"

assert FileInfo.normalize_name(" a.avi") == "a.avi"
assert FileInfo.normalize_name("a%a.avi") == "a.a.avi"
assert FileInfo.normalize_name("a..avi") == "a.avi"
assert FileInfo.normalize_name("a&.avi") == "a.avi"
assert FileInfo.normalize_name("a.-.b.avi") == "a-b.avi"
assert FileInfo.normalize_name("A.Choo.2020.BluRay.iPad.1080p.AAC.x264-CHDPAD") == "A.Choo.2020.BluRay.iPad.1080p.AAC.x264-CHDPAD"
assert FileInfo.normalize_name("Shoe^^^^^^.avi") == "Shoe.avi"
assert FileInfo.normalize_name("^^^^^^^Shoe^^^^^^.avi") == "Shoe.avi"

# a file
fi = FileInfo("/Users/osharabi/Development/personal/ojo/ojo/config.json", "/tmp", "/home/auto/media")
assert fi.origin_path == "/Users/osharabi/Development/personal/ojo/ojo/config.json"
assert fi.working_path == "/tmp"
assert fi.media_info_path == "/home/auto/media"
assert fi.is_file is True
assert fi.is_media_file is False
assert fi.parent_path == "/Users/osharabi/Development/personal/ojo/ojo"
assert fi.file_name == "config"
assert fi.file_extension == ".json"
assert fi.normalized_file_name == "config"
assert fi.nfo_file_path == "/home/auto/media/config.nfo"
assert fi.nzb_file_path == "/home/auto/media/config.nzb"
assert fi.rar_file_path == "/tmp/config.rar"
assert fi.rar_files_path_wildcard == "/tmp/config.*.rar"
assert fi.par_file_path == "/tmp/config.par"
assert fi.size_mb == 0

import os
this_dir = os.path.abspath(".")
funky_file_name = "It's Funky.txt"
source_path = os.path.join(this_dir, funky_file_name)
with open(source_path, "w") as f:
    fi = FileInfo(source_path, "/tmp_dir", "/media_dir")
try:
    assert fi.file_name == "Its Funky"
    assert fi.origin_path == os.path.join(this_dir, "Its Funky.txt")
    assert os.path.exists(fi.origin_path)
except Exception as e:
    print(e)
finally:
    if os.path.exists(fi.origin_path):
        os.remove(fi.origin_path)
    else:
        os.remove(source_path)


funky_dir_name = 'It"s Funky'
source_path = os.path.join(this_dir, funky_dir_name)
os.mkdir(source_path)
fi = FileInfo(source_path, "/tmp_dir", "/media_dir")
try:
    assert fi.file_name == "Its Funky"
    assert fi.origin_path == os.path.join(this_dir, "Its Funky")
    assert os.path.exists(fi.origin_path)
except Exception as e:
    print(e)
finally:
    if os.path.exists(fi.origin_path):
        os.rmdir(fi.origin_path)
    else:
        os.remove(source_path)

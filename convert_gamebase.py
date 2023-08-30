import os
import shutil
import zipfile
import pycdlib
import requests

from io import BytesIO

from rich.progress import Progress, DownloadColumn, TransferSpeedColumn, BarColumn, TimeRemainingColumn, \
    TaskProgressColumn, MofNCompleteColumn


DOWNLOAD_URL = "https://archive.org/download/gbc-v18/GBC_V18_01.iso"
FILENAME = "GBC_V18_01.iso"
FILELEN = 3547310080
TEMP_FOLDER = "tmp"
CHUNK_SIZE = 1024 * 1024  # 1 MB
MAX_BUCKET_SIZE = 255
ALLOWED_CHARS = "QWERTYUIOPASDFGHJKLZXCVBNM1234567890.,-()[]! "
MAX_NAME_LENGTH = 25
NUM_ARCHIVES = 28261


def create_sub_categories(games):
    sub_categories = {}
    for game in games:
        category_id = game["name"][:2]
        if category_id not in sub_categories:
            sub_categories[category_id] = []
        sub_categories[category_id].append(game)
    return sub_categories


def download_large_file(url, destination):
    print(f"Downloading {url} to {destination}")

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))

        with open(destination, 'wb') as file:
            with Progress(DownloadColumn(), BarColumn(), TaskProgressColumn(), TimeRemainingColumn(), TransferSpeedColumn()) as progress:
                task1 = progress.add_task(f"{FILENAME}", total=total_size)
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):  # Adjust chunk size as needed
                    file.write(chunk)
                    progress.update(task1, advance=len(chunk))

        print(f"Downloaded {url} to {destination}")
    else:
        print(f"Failed to download {url}, status code: {response.status_code}")

def get_nfo_value(header, lines):
    for line in lines:
        if line.startswith("%s:" % header):
            value = line.split(":")[1].strip().upper()
            value = ''.join(c for c in value if c in ALLOWED_CHARS)
            return value[:MAX_NAME_LENGTH]  # max length of 25 characters
    return None


def index_if_duplicate(name, games):
    index = 2
    name_with_index = name
    while name_with_index in games:
        name_with_index = f"{name}_{index}"
        index += 1

    return name_with_index


def get_category(game):
    initial = game["name"][0]
    if initial.isdigit():
        return "0-9"
    elif initial.isalpha():
        return initial.upper()
    else:
        return "Other"


def get_file_contents_by_extension(directory_path, extension):
    contents = []
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(extension.lower()):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                contents.append(file.readlines())
    return contents


def get_nfo_name(folder):
    nfo_files = get_file_contents_by_extension(folder, ".nfo")

    for nfo_file in nfo_files:
        game_name = get_nfo_value("Name", nfo_file) or get_nfo_value("Unique-ID", nfo_file)
        if game_name:
            return game_name

    return os.path.basename(folder)


def prepare_empty_directory(directory_path):
    try:
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)  # Remove all files and subdirectories
        os.makedirs(directory_path)  # Create the empty directory
    except Exception as e:
        print("An error occurred:", e)


def extract_game_archive(iso, archive):
    extracted = BytesIO()
    iso.get_file_from_iso_fp(extracted, iso_path=f"{archive}")  # ;1

    folder = f"{TEMP_FOLDER}{archive[:-4]}"
    prepare_empty_directory(folder)
    with zipfile.ZipFile(extracted, 'r') as zip_ref:
        zip_ref.extractall(folder)

    return folder


def get_game_archives(iso, directory):
    # print(f"Reading: {directory}")

    archives = []
    for child in iso.list_children(iso_path=directory):
        filename = child.file_identifier().decode("utf-8")
        if filename.endswith(".ZIP"):
            archives.append("%s%s" % (directory, filename))

    # print(f"  Found {len(archives)} archives")
    return archives


def get_game_directories(iso):
    directories = []
    for child in iso.list_children(iso_path='/GAMES/'):
        filename = child.file_identifier().decode("utf-8")
        if filename not in (".", ".."):
            directories.append("/GAMES/%s/" % filename)

    return directories


def create_bucket(category_id, bucket):
    os.makedirs("gamebase/%s" % category_id, exist_ok=True)
    for game in bucket:
        os.rename(game["folder"], "gamebase/%s/%s" % (category_id, game["name"]))


def process_bucket(category_id, bucket):
    bucket = sorted(bucket, key=lambda x: x["name"])
    create_bucket(category_id, bucket[:MAX_BUCKET_SIZE+1])

    index = 2
    while len(bucket) > MAX_BUCKET_SIZE:
        bucket = bucket[MAX_BUCKET_SIZE+1:]
        create_bucket("%s (%s)" % (category_id, index), bucket[:MAX_BUCKET_SIZE+1])


if __name__ == "__main__":
    print("Preparing directories: gamebase")
    prepare_empty_directory("gamebase")

    if os.path.exists(FILENAME):
        if os.path.getsize(FILENAME) != FILELEN:
            print(f"{FILENAME} exists but is not the correct size, deleting it and re-downloading")
            os.remove(FILENAME)
            download_large_file(DOWNLOAD_URL, FILENAME)
        else:
            print(f"{FILENAME} exists and is the correct size, skipping download")
    else:
        download_large_file(DOWNLOAD_URL, FILENAME)

    print(f"Opening ISO image: {FILENAME}")
    iso = pycdlib.PyCdlib()
    iso.open(FILENAME)

    print("Reading game directories")
    directories = get_game_directories(iso)

    print("Reading game archives from directories")
    archives = []
    for directory in directories:  # limit here
        archives.extend(get_game_archives(iso, directory))

    print(f"Found {len(archives)} archives")

    games = {}

    with Progress(MofNCompleteColumn(), BarColumn(), TaskProgressColumn(), TimeRemainingColumn()) as progress:
        task = progress.add_task("Extracting", total=NUM_ARCHIVES)

        for a in archives:
            # print(f"Processing: {a}", end=" -> ")

            folder = extract_game_archive(iso, a)

            name = get_nfo_name(folder)
            while name and name[0] in ".,-()[]! ":
                name = name[1:]
            if not name:
                name = "NO_NAME"
            name = index_if_duplicate(name, games)

            # print(f"{name}")
            games[name] = {"folder": folder, "name": name}

            progress.update(task, advance=1, refresh=True)

    print("Closing ISO image")
    iso.close()

    print("Dividing games to buckets and moving them to gamebase/")
    categories = {}
    for game in games.values():
        category_id = get_category(game)
        if category_id not in categories:
            categories[category_id] = []
        categories[category_id].append(game)

    for category_id, games in categories.items():
        if category_id == "0-9":
            for n in range(0, 10):
                process_bucket("0-9/%s" % n, [game for game in games if game["name"][0] == str(n)])
        elif category_id == "Other":
            process_bucket("Other", games)
        else:
            if len(games) <= MAX_BUCKET_SIZE:
                process_bucket(category_id, games)
            else:
                sub_categories = create_sub_categories(games)
                bucket = []
                bucket_id = None
                for sub_category_id, sub_games in sorted(sub_categories.items()):
                    if bucket_id:
                        if len(bucket) + len(sub_games) > MAX_BUCKET_SIZE:
                            process_bucket("%s/%s" % (category_id, bucket_id), bucket)
                            bucket.clear()
                            bucket_id = sub_category_id
                    else:
                        bucket_id = category_id
                    bucket.extend(sub_games)
                process_bucket("%s/%s" % (category_id, bucket_id), bucket)

    shutil.rmtree(TEMP_FOLDER)

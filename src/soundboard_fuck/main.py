import argparse
import curses
import logging
import sys
from pathlib import Path

from soundboard_fuck.data.sound import Sound
from soundboard_fuck.db.sqlitedb import SqliteDb
from soundboard_fuck.ui.screen import SoundboardScreen


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    db = SqliteDb()
    parser = argparse.ArgumentParser()

    mutex_group = parser.add_mutually_exclusive_group()
    mutex_group.add_argument("--list-categories", "-lc", action="store_true")
    mutex_group.add_argument("--list-sounds", "-ls", action="store_true")
    mutex_group.add_argument("--clear-orphans", action="store_true")

    subparsers = parser.add_subparsers()
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("path", nargs="+")
    add_parser.set_defaults(subparser="add")
    add_parser.add_argument("--duplicates", action="store_true", help="Add duplicate sounds")
    add_parser.add_argument("--category", nargs="?")

    args = parser.parse_args()
    subparser = args.subparser if hasattr(args, "subparser") else None

    if args.list_categories:
        for c in db.list_categories():
            sys.stdout.write(f"id={c.id}, name={c.name}, is default={c.is_default}\n")
    elif args.list_sounds:
        for s in db.list_sounds():
            sys.stdout.write(
                f"id={s.id}, name={s.name}, category={s.category_id}, duration={s.duration_ms}, "
                f"path={s.path}\n"
            )
    elif args.clear_orphans:
        for s in [s for s in db.list_sounds() if not s.path.exists()]:
            db.delete_sound(s.id)
            sys.stdout.write(f"Deleted {s.name}\n")
    elif subparser == "add":
        existing_paths = [s.path for s in db.list_sounds()]
        if args.category:
            category = db.get_category(args.category)
        else:
            category = db.get_or_create_default_category()
        for path in [Path(p).absolute() for p in args.path]:
            if not path.is_file():
                continue
            if path in existing_paths and not args.duplicates:
                sys.stderr.write(f"Not adding {path} (duplicate)\n")
                continue
            try:
                duration_ms = Sound.extract_duration_ms(path)
                db.create_sound(name=path.stem, path=path, category_id=category.id, duration_ms=duration_ms)
                sys.stdout.write(f"Added {path}\n")
            except Exception as e:
                logger.error("Error adding %s", path, exc_info=e)
    else:
        screen = SoundboardScreen(db=db)
        curses.wrapper(screen.attach_window)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import msgpack
import os
import re

BOUNDARY = u"==========\r\n"
DATA_FILE = u"clips.msgpack"
OUTPUT_DIR = u"output"


def get_sections(filename):
    with open(filename, 'r') as f:
        content = f.read().decode('utf-8')
    content = content.replace(u'\ufeff', u'')
    return content.split(BOUNDARY)


def get_clip(section):
    clip = {}

    lines = [l for l in section.split(u'\r\n') if l]
    if len(lines) != 3:
        return

    clip['book'] = lines[0]
    positions = re.search('#(\d+)', lines[1])
    position = positions.group(1)
    if not position:
        return

    clip['position'] = int(position)

    if lines[1].find(unicode('的笔记', 'utf-8')) > 0:
        prefix = u'评论: '
    elif lines[1].find(unicode('的标注', 'utf-8')) > 0:
        prefix = u'摘录: '
    else:
        prefix = u''
    clip['content'] = prefix + lines[2]

    return clip


def export_txt(clips):
    """
    Export each book's clips to single text.
    """
    for book in clips:
        lines = []
        for pos in sorted(clips[book]):
            lines.append('\n------\nloc (%05d), %s' % (pos, clips[book][pos].encode('utf-8')))

        filename = os.path.join(OUTPUT_DIR, u"%s.txt" % (book.replace(' ', '_')))
        with open(filename, 'w') as f:
            f.write("\n".join(lines))


def load_clips():
    """
    Load previous clips from DATA_FILE
    """
    try:
        with open(DATA_FILE, 'r') as f:
            return msgpack.unpack(f, encoding='utf-8')
    except IOError:
        return {}


def save_clips(clips):
    """
    Save new clips to DATA_FILE
    """
    with open(DATA_FILE, 'wb') as f:
        f.write(msgpack.packb(clips, encoding='utf-8'))


def main():
    # load old clips
    clips = collections.defaultdict(dict)
    clips.update(load_clips())

    # extract clips
    sections = get_sections(u'My Clippings.txt')
    for section in sections:
        clip = get_clip(section)
        if clip:
            clips[clip['book']][clip['position']] = clip['content']

    # remove key with empty value
    clips = {k: v for k, v in clips.iteritems() if v}

    # save/export clips
    save_clips(clips)
    export_txt(clips)


if __name__ == '__main__':
    main()

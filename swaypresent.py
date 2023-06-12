#!/usr/bin/python

#    Copyright 2023 Dorian Rudolph
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


import i3ipc
import argparse
import sys
import subprocess


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def check_overlap(r1, r2):
    return not (r1.x >= r2.x + r2.width or
                r1.x + r1.width <= r2.x or
                r1.y >= r2.y + r2.height or
                r1.y + r1.height <= r2.y)


def main():
    parser = argparse.ArgumentParser(
        prog='swaypresent.py',
        description='Launch wl-mirror on a new workspace in fullscreen')
    parser.add_argument('-s', '--source', help='The output to mirror (default: first)')
    parser.add_argument('-d', '--destination', help='The output where the mirror is displayed (default: second)')
    parser.add_argument('-w', '--workspace', default='p', help='Name of workspace where mirror will be displayed')
    parser.add_argument('-o', '--fix-overlapping', action='store_true', help='Fix overlapping outputs')
    parser.add_argument('-r', '--match-ratio', action='store_true', help='Set aspect ratio of source output to match destination output')
    args = parser.parse_args()

    i3 = i3ipc.Connection()
    outputs = i3.get_outputs()
    if len(outputs) < 2:
        eprint('Need at least two outputs for mirroring.')
        exit(1)

    src_output = args.source
    dst_output = args.destination
    if not src_output:
        src_output = [o for o in outputs if o.name != dst_output][0].name
    if not dst_output:
        dst_output = [o for o in outputs if o.name != src_output][0].name

    src = [o for o in outputs if o.name == src_output]
    dst = [o for o in outputs if o.name == dst_output]
    if not src:
        eprint(f'Source output "{src_output}" not found.')
        exit(1)
    if not dst:
        eprint(f'Destination output "{dst_output}" not found.')
        exit(1)
    src = src[0]
    dst = dst[0]

    if args.match_ratio:
        w = src.rect.width
        h = src.rect.height
        a_src = w / h
        a_dst = dst.rect.width / dst.rect.height
        change = False
        if a_src < a_dst - 0.01:
            h = int(round(w / a_dst))
            change = True
        elif a_src > a_dst + 0.01:
            w = int(round(h * a_dst))
            change = True
        if change:
            i3.command(f'output {src_output} mode --custom {w}x{h}')
            src = [o for o in i3.get_outputs() if o.name == src_output][0]

    if args.fix_overlapping and check_overlap(src.rect, dst.rect):
        i3.command(f'output {src_output} position '
                   f'{dst.rect.x + (dst.rect.width - src.rect.width) // 2} {dst.rect.y + dst.rect.height}')


    i3.command('workspace p')
    i3.command(f'move workspace output {dst_output}')

    def on_window_new(i3, event):
        if event.container.app_id == 'at.yrlf.wl_mirror':
            i3.command(f'[con_id={event.container.id}] fullscreen')
            i3.command(f'focus output {src_output}')
            i3.main_quit()

    i3.on('window::new', on_window_new)
    subprocess.Popen(['wl-present', 'mirror', src_output])
    i3.main()


if __name__ == '__main__':
    main()

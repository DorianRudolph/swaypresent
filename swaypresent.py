#!/usr/bin/python

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
    parser.add_argument('-f', '--fix-overlapping', action='store_true', help='Fix overlapping outputs')
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

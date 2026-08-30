import curses
import time
import psutil

REFRESH = 0.7


def get_procs():
    procs = []
    for p in psutil.process_iter(["pid", "name"]):
        try:
            info = p.info
            cpu = p.cpu_percent(None)
            mem = p.memory_percent()
            procs.append({
                "pid": info["pid"],
                "name": info["name"] or "?",
                "cpu": cpu,
                "mem": mem,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    procs.sort(key=lambda p: p["cpu"], reverse=True)
    return procs


def bar(pct, width=20):
    filled = int(width * min(pct, 100) / 100)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def draw(scr, procs):
    h, w = scr.getmaxyx()
    scr.erase()

    cpu_total = psutil.cpu_percent(None)
    vmem = psutil.virtual_memory()

    scr.addstr(0, 0, " GRAND LINE MONITOR ".center(w - 1), curses.color_pair(1))
    scr.addstr(1, 0, f"CPU: {bar(cpu_total)} {cpu_total:5.1f}%"[:w - 1])

    used_gb = vmem.used / (1024 ** 3)
    total_gb = vmem.total / (1024 ** 3)
    scr.addstr(2, 0, f"MEM: {bar(vmem.percent)} {vmem.percent:5.1f}% ({used_gb:.1f}G / {total_gb:.1f}G)"[:w - 1])

    header_row = 4
    scr.addstr(header_row, 0, f"{'PID':>7}  {'CPU%':>6}  {'MEM%':>6}  NAME"[:w - 1], curses.color_pair(1) | curses.A_BOLD)

    list_top = header_row + 1
    list_bottom = h - 2
    rows = max(0, list_bottom - list_top)

    for i in range(rows):
        if i >= len(procs):
            break
        p = procs[i]
        line = f"{p['pid']:>7}  {p['cpu']:6.1f}  {p['mem']:6.1f}  {p['name']}"
        line = line[:w - 1]

        attr = curses.A_NORMAL
        if p["cpu"] > 50:
            attr = curses.color_pair(5)
        elif p["cpu"] > 15:
            attr = curses.color_pair(4)

        try:
            scr.addstr(list_top + i, 0, line.ljust(w - 1), attr)
        except curses.error:
            pass

    footer = f" total processes: {len(procs)}   [q] quit "
    scr.addstr(h - 1, 0, footer[:w - 1].ljust(w - 1), curses.color_pair(1))

    scr.refresh()


def main(scr):
    curses.curs_set(0)
    scr.nodelay(True)
    scr.timeout(int(REFRESH * 1000))

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)
    curses.init_pair(5, curses.COLOR_RED, -1)

    for p in psutil.process_iter():
        try:
            p.cpu_percent(None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    while True:
        procs = get_procs()
        draw(scr, procs)

        try:
            key = scr.getch()
        except curses.error:
            key = -1

        if key == ord("q"):
            break


if __name__ == "__main__":
    curses.wrapper(main)

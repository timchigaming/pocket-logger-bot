import logging, html, os, time, subprocess, platform as pt, psutil as ps, datetime, asyncio
from asyncio.subprocess import Process

#------VARS------
OS_NAME = os.name
executing_shells: list[tuple[str, int, Process]] = []
#----------------

#----------------#----------------#----------------
async def execute_internal(cmd: str, safe_output = True, max_symbols_per_log = 1500):
    if not cmd: logging.error(f"execute_internal() called with an invalid set of arguments: {cmd}")

    then = time.time()
    process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    process_packed = (cmd, process.pid, process)

    executing_shells.append(process_packed)

    try:
        proc_result = await process.communicate()
    finally:
        executing_shells.remove(process_packed)

    now = time.time()
    dt = f"{((now - then)):.0f}"    
    
    safe_cmd = html.escape(cmd)
    safe_stdout = html.escape(proc_result[0].decode("cp866" if OS_NAME=="nt" else "utf-8").strip())
    safe_stderr = html.escape(proc_result[1].decode("cp866" if OS_NAME=="nt" else "utf-8").strip())

    if safe_output:
        if len(safe_stdout) > max_symbols_per_log:
            safe_stdout = safe_stdout[:max_symbols_per_log] + "\n[... (Достигнуто МАКС количество символов в потоке вывода) ...]"
        if len(safe_stderr) > max_symbols_per_log:
            safe_stderr = safe_stderr[:max_symbols_per_log] + "\n[... (Достигнуто МАКС количество символов в потоке вывода) ...]"

    text = \
f"""\
Запрос <code class="language-sh">{safe_cmd}</code> был обработан за <code>{dt}</code> секунд,
STDOUT:
<pre><code class="language-sh">{safe_stdout}</code></pre>
STDERR:
<pre><code class="language-sh"> {safe_stderr} </code></pre>
Return code <code>{process.returncode}</code>.
"""
    return text

async def halt_execute_internal(pid):
    pid_str = str(pid)
    kill_cmd = "taskkill /F /T /PID " + pid_str if OS_NAME=="nt" else "pkill -9 -P " + pid_str

    for pack in executing_shells:
        cmd, _pid, process = pack
        if _pid != pid: continue
        
        subprocess.run(kill_cmd)
        return await process.wait()
    return 0
#----------------#----------------

def procentage_bar(value, delimeter = 100, width = 10):
    if value < 1:
        return "░" * width

    fill_percent = delimeter / value * 100
    
    fill: int = int( 100 / fill_percent * width)
    semi_transparent: int = (100 * width) % int(fill_percent) > 1
    empty: int = width - fill
    
    return ("█" * fill) + ("▓" * semi_transparent) + ("░" * empty)

server_name = "SERVER" # После, когда будет SSH, заменим на его ключевое имя по 
def system_info_internal():
    def get_disks_info():
        disks_info = ""
        for device, _, fstype, _ in ps.disk_partitions():
            try:
                disk_volume = ps.disk_usage(device)
                disk_load = procentage_bar(disk_volume.percent)
                disks_info += f"-\tДиск {device: <10}, ФС: {fstype: <7}, Занято {disk_volume.used//1024**2: >6.0f}МБ из {disk_volume.total//1024**2: >6.0f}МБ—[{disk_load}]\n"
            except (PermissionError, OSError):
                continue # Устройство может быть "не готово". Ну и че? Пропускаем значит.
        return disks_info
    
    time_since_bootup = str(datetime.timedelta(seconds=int(time.time() - ps.boot_time())))
    vm = ps.virtual_memory()
    virtual_memory_load = procentage_bar(vm.percent)
    disks_info = get_disks_info()
    
    text = \
f"""\
Статы {server_name}:
<b>ЦПУ</b>: 
    Название: <code>{pt.processor()}</code>
    Ядер {ps.cpu_count()}, Частота: {ps.cpu_freq()[0]:.0f}МГц, 
    Время работы: {time_since_bootup}, Загруженность СЕЙЧАС: {ps.cpu_percent(interval=0.1)}% в общем.
<b>ОЗУ</b>:
    Всего {int(vm.total/1024**2):.0f}МБ, Используется {int(vm.used/1024**2):.0f}МБ—<code>[{virtual_memory_load}]</code>
<b>ДИСКИ</b>:\n<pre><code class="language-sh">{disks_info}</code></pre>
"""
    return text

#----------------#----------------#----------------

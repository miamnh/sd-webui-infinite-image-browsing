from datetime import datetime
import os
import platform
import re
import tempfile
import imghdr



def human_readable_size(size_bytes):
    """
    Converts bytes to a human-readable format.
    """
    # define the size units
    units = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    # calculate the logarithm of the input value with base 1024
    size = int(size_bytes)
    if size == 0:
        return '0B'
    i = 0
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    # round the result to two decimal points and return as a string
    return '{:.2f} {}'.format(size, units[i])

def get_windows_drives():
    drives = []
    for drive in range(ord('A'), ord('Z')+1):
        drive_name = chr(drive) + ':/'
        if os.path.exists(drive_name):
            drives.append(drive_name)
    return drives

pattern = re.compile(r'(\d+\.?\d*)([KMGT]?B)', re.IGNORECASE)
def convert_to_bytes(file_size_str):
    match = re.match(pattern, file_size_str)
    if match:
        size_str, unit_str = match.groups()
        size = float(size_str)
        unit = unit_str.upper()
        if unit == "KB":
            size *= 1024
        elif unit == "MB":
            size *= 1024**2
        elif unit == "GB":
            size *= 1024**3
        elif unit == "TB":
            size *= 1024**4
        return int(size)
    else:
        raise ValueError(f"Invalid file size string '{file_size_str}'")
    

import asyncio


def debounce(delay):
    """用于优化高频事件的装饰器"""
    
    def decorator(func):
        from typing import Union
        task: Union[None, asyncio.Task] = None

        async def debounced(*args, **kwargs):
            nonlocal task
            if task:
                task.cancel()
            task = asyncio.create_task(asyncio.sleep(delay))
            await task
            return await func(*args, **kwargs)

        return debounced

    return decorator


def is_valid_image_path(path):
    """
    判断给定的路径是否是图像文件
    """
    abs_path = os.path.abspath(path)  # 转为绝对路径
    if not os.path.exists(abs_path):  # 判断路径是否存在
        return False
    if not os.path.isfile(abs_path):  # 判断是否是文件
        return False
    if not imghdr.what(abs_path):  # 判断是否是图像文件
        return False
    return True


is_dev = "APP_ENV" in os.environ and os.environ["APP_ENV"] == "dev"
cwd = os.path.normpath(os.path.join(__file__, "../../"))
is_win = platform.system().lower().find("windows") != -1


def get_temp_path():
    """获取跨平台的临时文件目录路径"""
    temp_path = None
    try:
        # 尝试获取系统环境变量中的临时文件目录路径
        temp_path = os.environ.get('TMPDIR') or os.environ.get('TMP') or os.environ.get('TEMP')
    except Exception as e:
        print("获取系统环境变量临时文件目录路径失败，错误信息：", e)

    # 如果系统环境变量中没有设置临时文件目录路径，则使用 Python 的 tempfile 模块创建临时文件目录
    if not temp_path:
        try:
            temp_path = tempfile.gettempdir()
        except Exception as e:
            print("使用 Python 的 tempfile 模块创建临时文件目录失败，错误信息：", e)

    # 确保临时文件目录存在
    if not os.path.exists(temp_path):
        try:
            os.makedirs(temp_path)
        except Exception as e:
            print("创建临时文件目录失败，错误信息：", e)

    return temp_path

temp_path = get_temp_path()


def get_locale():
    import locale
    lang, _ = locale.getdefaultlocale()
    return 'zh' if lang.startswith('zh') else 'en'

locale = get_locale()

def get_modified_date(folder_path):
    return datetime.fromtimestamp(os.path.getmtime(folder_path)).strftime('%Y-%m-%d %H:%M:%S')


def unique_by(seq, key_func):
    seen = set()
    return [x for x in seq if not (key := key_func(x)) in seen and not seen.add(key)]

def read_info_from_image(image) -> str:    
    import piexif
    import piexif.helper
    items = image.info or {}
    geninfo = items.pop('parameters', None)
    if "exif" in items:
        exif = piexif.load(items["exif"])
        exif_comment = (exif or {}).get("Exif", {}).get(piexif.ExifIFD.UserComment, b'')
        try:
            exif_comment = piexif.helper.UserComment.load(exif_comment)
        except ValueError:
            exif_comment = exif_comment.decode('utf8', errors="ignore")

        if exif_comment:
            items['exif comment'] = exif_comment
            geninfo = exif_comment
    return geninfo

re_param_code = r'\s*([\w ]+):\s*("(?:\\"[^,]|\\"|\\|[^\"])+"|[^,]*)(?:,|$)'
re_param = re.compile(re_param_code)
re_imagesize = re.compile(r"^(\d+)x(\d+)$")
re_lora_prompt = re.compile("<lora:([\w_]+):([\d.]+)>")
re_parens = re.compile(r'[\\/\[\](){}]+')

def parse_prompt(x:str):
    x = re.sub(re_parens, '', x.lower().replace('，',',').replace('-',' ').replace('_', ' '))
    tag_list = [x.strip() for x in x.split(',')]
    res = []
    lora_list = []
    for tag in tag_list:
        if len(tag) == 0:
            continue
        idx_colon = tag.find(':')
        if idx_colon != -1:
            lora_res = re.match(re_lora_prompt, tag)
            if lora_res:
                lora_list.append({ "name": lora_res.group(1), "value": float(lora_res.group(2))})
            else:
              res.append(tag[0:idx_colon])
        else:
            res.append(tag)
    return res, lora_list

def parse_generation_parameters(x: str):
    res = {}
    prompt = ""
    negative_prompt = ""
    done_with_prompt = False
    *lines, lastline = x.strip().split("\n")
    if len(re_param.findall(lastline)) < 3:
        lines.append(lastline)
        lastline = ''

    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("Negative prompt:"):
            done_with_prompt = True
            line = line[16:].strip()

        if done_with_prompt:
            negative_prompt += ("" if negative_prompt == "" else "\n") + line
        else:
            prompt += ("" if prompt == "" else "\n") + line

    #res["pos_prompt"] = prompt
    #res["neg_prompt"] = negative_prompt

    for k, v in re_param.findall(lastline):
        v = v[1:-1] if v[0] == '"' and v[-1] == '"' else v
        m = re_imagesize.match(v)
        if m is not None:
            res[k+"-1"] = m.group(1)
            res[k+"-2"] = m.group(2)
        else:
            res[k] = v
    pos_prompt, lora = parse_prompt(prompt)
    neg_prompt = [] # parse_prompt(negative_prompt)[0]
    for k in res:
        k_s = str(k)
        if k_s.startswith("AddNet Module") and str(res[k]).lower() == "lora":
            model = res[k_s.replace("Module", "Model")]
            value = res.get(k_s.replace("Module", "Weight A"), "1")
            lora.append({ "name": model, "value": float(value) })
    return res, unique_by(lora, lambda x:x.name), unique_by(pos_prompt, lambda x:x), unique_by(neg_prompt, lambda x:x)


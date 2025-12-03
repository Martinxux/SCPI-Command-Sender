# 修复文件末尾的换行符
with open('scpi_app/core/scpi.py', 'r+', encoding='utf-8') as f:
    content = f.read()
    if not content.endswith('\n'):
        f.seek(0, 2)
        f.write('\n')
        print("已添加文件末尾换行符")
    else:
        print("文件末尾已存在换行符")

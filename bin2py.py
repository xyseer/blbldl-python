# -*- coding: utf-8 -*-
"""以python模块形式存储、使用二进制文件"""
import os
import base64
from io import BytesIO
import sys
def bin2module(bin_file, py_file=None):
  """二进制文件转存为python模块
  bin_file  - 二进制文件名
  py_file   - 生成的模块文件名，默认使用二进制文件名，仅更改后缀名
  """
  fpath, fname = os.path.split(bin_file)
  fn, ext = os.path.splitext(fname)
  if not py_file:
    py_file = os.path.join(fpath, '%s.py'%fn)
  with open(bin_file, 'rb') as fp:
    content = fp.read()
  content = base64.b64encode(content)
  content = content.decode('utf8')
  with open(py_file, 'w') as fp:
    fp.write('# -*- coding: utf-8 -*-\n\n')
    fp.write('import base64\n')
    fp.write('from io import BytesIO\n\n')
    fp.write('content = """%s"""\n\n'%content)
    fp.write('def get_fp():\n')
    fp.write('  return BytesIO(base64.b64decode(content.encode("utf8")))\n\n')
    fp.write('def save(file_name):\n')
    fp.write('  with open(file_name, "wb") as fp:\n')
    fp.write('    fp.write(base64.b64decode(content.encode("utf8")))\n')
if __name__ == '__main__':
  """测试代码"""
  # 将图像文件转存为img_demo.py
  
  bin2module(sys.argv[1], sys.argv[1]+'.py')
  # 导入刚刚生成的demo模块
  exec('import '+sys.argv[1]+"as demo")
  # 用pillow打开图像，验证demo模块的get_fp()：返回二进制的IO对象（类文件对象）
  from PIL import Image
  im = Image.open(demo.get_fp())
  im.show()
  # 保存为本地文件，验证demo模块的save()：保存文件
  #demo.save('demo_save.png')

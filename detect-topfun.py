import os
import ast
import sys
import subprocess
from collections import defaultdict
import shutil

try:
    from stdlib_list import stdlib_list
except ImportError:
    print("正在安装依赖库 'stdlib-list'...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'stdlib-list'], check=True)
    from stdlib_list import stdlib_list

# 常见模块名到PyPI包名的映射
MODULE_TO_PACKAGE = {
    'PIL': 'Pillow',
    'sklearn': 'scikit-learn',
    'yaml': 'PyYAML',
    'bs4': 'beautifulsoup4',
    'MySQLdb': 'mysqlclient',
    '_curses': 'curses',
    'cv2': 'opencv-python',
    'jieba': 'jieba',
    'dateutil': 'python-dateutil',
}

def find_py_files(directory):
    """查找目录下所有.py文件"""
    py_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))
    return py_files

def get_local_modules(directory):
    """获取项目中所有本地模块名（不带.py后缀的文件名）"""
    local_modules = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                module_name = os.path.splitext(file)[0]
                if module_name != "__init__":
                    local_modules.add(module_name)
    return local_modules

def extract_imports(file_path, local_modules):
    """从单个文件中提取所有导入的顶级模块（排除本地模块）"""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=file_path)
    except (SyntaxError, UnicodeDecodeError):
        return imports
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name.split('.')[0]
                if module and module not in local_modules:
                    imports.add(module)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module = node.module.split('.')[0]
                if module and module not in local_modules:
                    imports.add(module)
    return imports

def get_project_imports(directory, local_modules):
    """获取项目中所有第三方导入（排除本地模块）"""
    all_imports = set()
    for py_file in find_py_files(directory):
        all_imports.update(extract_imports(py_file, local_modules))
    return all_imports

def is_stdlib_module(module_name):
    """判断模块是否属于标准库"""
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    try:
        std_modules = stdlib_list(version)
    except Exception:
        std_modules = stdlib_list("3.9")  # 回退机制
    return module_name in std_modules

def resolve_package_name(module_name):
    """将模块名转换为PyPI包名"""
    return MODULE_TO_PACKAGE.get(module_name, module_name)

def install_packages(packages):
    """尝试安装所有包并记录结果"""
    # 先检查并修复pip环境
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'check'], check=True)
    except subprocess.CalledProcessError:
        print("发现损坏的包，尝试修复...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--force-reinstall', 'setuptools'])
    
    results = defaultdict(dict)
    for pkg in packages:
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--no-cache-dir', pkg],
                capture_output=True,
                text=True,
                timeout=120,
                check=True
            )
            results[pkg] = {
                'success': True,
                'message': result.stdout.strip() or "安装成功"
            }
        except Exception as e:
            results[pkg] = {
                'success': False,
                'message': str(e.stderr).strip() if hasattr(e, 'stderr') else str(e)
            }
    return results

def generate_report(results):
    """生成安装报告"""
    success = []
    failed = []
    
    for pkg, data in results.items():
        if data['success']:
            success.append(pkg)
        else:
            failed.append({'package': pkg, 'reason': data['message']})
    
    print("\n安装结果:")
    print(f"成功安装 {len(success)} 个包:")
    for pkg in success:
        print(f"  ✓ {pkg}")
    
    if failed:
        print(f"\n{len(failed)} 个包安装失败:")
        for item in failed:
            print(f"  ✗ {item['package']}: {item['reason'][:200]}...")

def main(project_dir):
    # 获取所有本地模块名
    local_modules = get_local_modules(project_dir)
    print(f"发现 {len(local_modules)} 个本地模块: {', '.join(sorted(local_modules)[:5])}..." if local_modules else "未发现本地模块")
    
    # 获取所有导入
    imports = get_project_imports(project_dir, local_modules)
    print(f"检测到 {len(imports)} 个唯一第三方导入模块")
    
    # 过滤标准库
    third_party = [m for m in imports if not is_stdlib_module(m)]
    print(f"过滤后剩余 {len(third_party)} 个需要安装的第三方模块")
    
    # 转换模块名为包名
    packages = list(set([resolve_package_name(m) for m in third_party]))
    print(f"尝试安装以下包: {', '.join(packages)}")
    
    # 安装包
    if not packages:
        print("没有需要安装的第三方包")
        return
    
    results = install_packages(packages)
    generate_report(results)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python dep_installer.py <项目目录>")
        sys.exit(1)
    
    project_directory = sys.argv[1]
    if not os.path.isdir(project_directory):
        print(f"错误: 目录 '{project_directory}' 不存在")
        sys.exit(1)
    
    main(project_directory)
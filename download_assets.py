"""
اسکریپت دانلود فایل‌های استاتیک همیار فرش
این اسکریپت فقط یک بار اجرا شود!
python download_assets.py
"""
import os
import urllib.request
import zipfile
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

def download(url, dest):
    if os.path.exists(dest):
        print(f'  [SKIP] {os.path.basename(dest)} already exists')
        return
    print(f'  [DOWN] {os.path.basename(dest)} ...')
    urllib.request.urlretrieve(url, dest)
    size = os.path.getsize(dest) / 1024
    print(f'         OK ({size:.0f} KB)')

def main():
    print('='*50)
    print(' دانلود فایل‌های استاتیک همیار فرش')
    print('='*50)

    # --- Bootstrap 5.3 RTL ---
    print('\n[1/4] Bootstrap 5.3 RTL ...')
    css_dir = os.path.join(STATIC_DIR, 'css')
    js_dir = os.path.join(STATIC_DIR, 'js')
    download(
        'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.rtl.min.css',
        os.path.join(css_dir, 'bootstrap.rtl.min.css')
    )
    download(
        'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js',
        os.path.join(js_dir, 'bootstrap.bundle.min.js')
    )

    # --- Chart.js ---
    print('\n[2/4] Chart.js ...')
    download(
        'https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js',
        os.path.join(js_dir, 'chart.umd.min.js')
    )

    # --- Vazirmatn Font ---
    print('\n[3/4] Vazirmatn Font (Farsi Digits) ...')
    fonts_dir = os.path.join(STATIC_DIR, 'fonts', 'vazirmatn')
    os.makedirs(fonts_dir, exist_ok=True)

    zip_path = os.path.join(STATIC_DIR, 'fonts', 'vazirmatn_temp.zip')
    extract_dir = os.path.join(STATIC_DIR, 'fonts', 'vazirmatn_temp')

    # Check if fonts already downloaded
    if os.path.exists(os.path.join(fonts_dir, 'Vazirmatn-FD-Regular.woff2')):
        print('  [SKIP] Vazirmatn fonts already exist')
    else:
        download(
            'https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/vazirmatn-v33.003.zip',
            zip_path
        )
        print('  [EXTRACT] Extracting fonts ...')
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_dir)

        # Copy Farsi Digits webfonts
        fd_woff2_dir = os.path.join(extract_dir, 'misc', 'Farsi-Digits', 'fonts', 'webfonts')
        fd_ttf_dir = os.path.join(extract_dir, 'misc', 'Farsi-Digits', 'fonts', 'ttf')

        wanted_weights = ['Regular', 'Medium', 'Bold', 'SemiBold', 'Light', 'Black']
        for w in wanted_weights:
            src = os.path.join(fd_woff2_dir, f'Vazirmatn-FD-{w}.woff2')
            if os.path.exists(src):
                shutil.copy2(src, fonts_dir)
                print(f'  [COPY] Vazirmatn-FD-{w}.woff2')

        # Copy TTF for Pillow image processing
        for w in ['Regular', 'Bold']:
            src = os.path.join(fd_ttf_dir, f'Vazirmatn-FD-{w}.ttf')
            if os.path.exists(src):
                shutil.copy2(src, fonts_dir)
                print(f'  [COPY] Vazirmatn-FD-{w}.ttf')
            else:
                # Fallback: copy main TTF
                main_ttf = os.path.join(extract_dir, 'fonts', 'ttf', f'Vazirmatn-{w}.ttf')
                if os.path.exists(main_ttf):
                    shutil.copy2(main_ttf, os.path.join(fonts_dir, f'Vazirmatn-FD-{w}.ttf'))
                    print(f'  [COPY] Vazirmatn-{w}.ttf -> Vazirmatn-FD-{w}.ttf')

        # Cleanup
        os.remove(zip_path)
        shutil.rmtree(extract_dir)
        print('  [CLEAN] Temp files removed')

    # --- Bootstrap Icons (optional but nice) ---
    print('\n[4/4] Bootstrap Icons ...')
    download(
        'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css',
        os.path.join(css_dir, 'bootstrap-icons.min.css')
    )
    # Icon fonts
    icon_fonts_dir = os.path.join(STATIC_DIR, 'fonts')
    download(
        'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/fonts/bootstrap-icons.woff2',
        os.path.join(icon_fonts_dir, 'bootstrap-icons.woff2')
    )
    download(
        'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/fonts/bootstrap-icons.woff',
        os.path.join(icon_fonts_dir, 'bootstrap-icons.woff')
    )

    print('\n' + '='*50)
    print(' تمام فایل‌ها با موفقیت دانلود شدند!')
    print('='*50)
    print(f'\nمسیر: {STATIC_DIR}')

if __name__ == '__main__':
    main()

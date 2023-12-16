import requests
import m3u8
import os
import time


def download_segment(url, max_retries=3):
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    """嘗試下載單個 ts 段落，如果失敗則重試。"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10, headers=headers)
            if response.status_code == 200:
                return response.content
            else:
                print(
                    f"Error downloading {url}: Status code {response.status_code}"
                )
        except requests.RequestException as e:
            print(f"Error downloading {url}: {e}")

        time.sleep(2**attempt)  # 指數退避策略

    return None  # 如果所有重試都失敗


def download_and_save_individual_ts_files(m3u8_url,
                                          merged_output_file,
                                          individual_files_dir,
                                          min_size_kb=10):
    # 確保儲存單獨檔案的目錄存在
    if not os.path.exists(individual_files_dir):
        os.makedirs(individual_files_dir)

    # 解析 M3U8 文件
    m3u8_obj = m3u8.load(m3u8_url)

    with open(merged_output_file, 'wb') as merged_file:
        for i, segment in enumerate(m3u8_obj.segments):
            ts_url = segment.uri
            ts_content = download_segment(ts_url)

            if ts_content and len(ts_content) >= min_size_kb * 1024:
                # 從 URL 提取原始檔案名
                original_filename = ts_url.split("/")[-1]
                # 儲存每個單獨的 ts 段落，檔案名後綴為原始檔案名
                individual_filename = os.path.join(
                    individual_files_dir, f'segment_{i}_{original_filename}')
                with open(individual_filename, 'wb') as individual_file:
                    individual_file.write(ts_content)

                # 合併檔案
                merged_file.write(ts_content)
            else:
                print(
                    f"Segment {ts_url} is too small or failed to download, skipping."
                )
            time.sleep(1)

    print(
        f'All segments have been processed and saved into {merged_output_file}'
    )


# 讀取 M3U8 網址
with open('m3u8_url.txt', 'r') as file:
    m3u8_url = file.read().strip()

# 使用範例
merged_output_file = 'merged_video.ts'
individual_files_dir = 'individual_segments'
download_and_save_individual_ts_files(m3u8_url, merged_output_file,
                                      individual_files_dir)

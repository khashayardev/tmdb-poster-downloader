# download_movie_posters_by_year.py
import requests
import json
import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Optional
import zipfile
import io

class TMDBPosterDownloader:
    def __init__(self, access_token: str):
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/original"  # کیفیت اصلی
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json;charset=utf-8"
        }
        self.stats = {
            'total_movies': 0,
            'downloaded_posters': 0,
            'failed_posters': 0,
            'years_processed': 0,
            'api_calls': 0
        }

    def fetch_movies_by_year(self, year: int, min_votes: int = 0, min_rating: float = 0, limit: int = 1000) -> List[Dict]:
        """دریافت لیست فیلم‌های یک سال (بدون فیلتر امتیاز برای دریافت همه)"""
        params = {
            "primary_release_year": year,
            "sort_by": "popularity.desc",
            "vote_count.gte": min_votes,
            "include_adult": False
        }
        
        print(f"   🔍 دریافت لیست فیلم‌های سال {year}...")
        
        all_movies = []
        page = 1
        max_pages = 50  # حداکثر 50 صفحه = 1000 فیلم
        
        while page <= max_pages and len(all_movies) < limit:
            params['page'] = page
            try:
                resp = requests.get(f"{self.base_url}/discover/movie", headers=self.headers, params=params, timeout=15)
                self.stats['api_calls'] += 1
                
                if resp.status_code == 200:
                    data = resp.json()
                    movies = data.get('results', [])
                    if not movies:
                        break
                    all_movies.extend(movies)
                    total_pages = min(data.get('total_pages', 1), max_pages)
                    print(f"      📄 صفحه {page}/{total_pages} - {len(movies)} فیلم (مجموع: {len(all_movies)})")
                    page += 1
                    time.sleep(0.1)
                elif resp.status_code == 429:
                    print(f"      ⚠️ Rate limit! 2 ثانیه صبر...")
                    time.sleep(2)
                else:
                    print(f"      ⚠️ خطا {resp.status_code}")
                    break
            except Exception as e:
                print(f"      ❌ خطا: {e}")
                break
        
        print(f"   ✅ {len(all_movies)} فیلم برای سال {year} پیدا شد")
        return all_movies

    def get_imdb_id(self, movie_id: int) -> Optional[str]:
        """دریافت IMDB ID فیلم"""
        try:
            resp = requests.get(
                f"{self.base_url}/movie/{movie_id}/external_ids",
                headers=self.headers,
                timeout=15
            )
            self.stats['api_calls'] += 1
            if resp.status_code == 200:
                data = resp.json()
                return data.get('imdb_id')
            return None
        except Exception as e:
            print(f"      ❌ خطا در دریافت IMDB ID: {e}")
            return None

    def download_poster(self, poster_path: str, imdb_id: str, year: int, output_dir: str) -> bool:
        """دانلود پوستر فیلم و ذخیره با نام IMDB ID"""
        if not poster_path or not imdb_id:
            return False
        
        # نام فایل: imdb_id.jpg
        filename = f"{imdb_id}.jpg"
        filepath = os.path.join(output_dir, filename)
        
        # اگر فایل قبلاً دانلود شده،跳过
        if os.path.exists(filepath):
            print(f"      ⏭️ فایل از قبل وجود دارد: {filename}")
            return True
        
        image_url = f"{self.image_base_url}{poster_path}"
        
        try:
            resp = requests.get(image_url, timeout=30, stream=True)
            if resp.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in resp.iter_content(1024):
                        f.write(chunk)
                return True
            else:
                print(f"      ❌ خطا در دانلود {imdb_id}: HTTP {resp.status_code}")
                return False
        except Exception as e:
            print(f"      ❌ خطا در دانلود {imdb_id}: {e}")
            return False

    def process_year(self, year: int, output_base_dir: str):
        """پردازش کامل یک سال: دریافت لیست و دانلود پوسترها"""
        print(f"\n📅 شروع پردازش سال {year}")
        print("="*50)
        
        # ایجاد پوشه سال
        year_dir = os.path.join(output_base_dir, str(year))
        os.makedirs(year_dir, exist_ok=True)
        
        # مرحله 1: دریافت لیست فیلم‌های سال
        movies = self.fetch_movies_by_year(year, limit=1000)
        
        if not movies:
            print(f"   ⚠️ هیچ فیلمی برای سال {year} پیدا نشد")
            return
        
        # مرحله 2: برای هر فیلم، IMDB ID را بگیر و پوستر را دانلود کن
        total = len(movies)
        downloaded = 0
        failed = 0
        
        for i, movie in enumerate(movies, 1):
            movie_id = movie['id']
            title = movie.get('title', 'Unknown')
            poster_path = movie.get('poster_path')
            
            print(f"   🔄 [{i}/{total}] {title[:50]}...")
            
            # دریافت IMDB ID
            imdb_id = self.get_imdb_id(movie_id)
            
            if imdb_id and poster_path:
                success = self.download_poster(poster_path, imdb_id, year, year_dir)
                if success:
                    downloaded += 1
                    print(f"      ✅ دانلود شد: {imdb_id}.jpg")
                else:
                    failed += 1
            elif not imdb_id:
                print(f"      ⚠️ IMDB ID پیدا نشد")
                failed += 1
            elif not poster_path:
                print(f"      ⚠️ پوستر موجود نیست")
                failed += 1
            
            # تاخیر برای جلوگیری از Rate Limit
            time.sleep(0.2)
        
        # به‌روزرسانی آمار
        self.stats['years_processed'] += 1
        self.stats['total_movies'] += total
        self.stats['downloaded_posters'] += downloaded
        self.stats['failed_posters'] += failed
        
        print(f"\n   📊 آمار سال {year}:")
        print(f"      ✅ دانلود شده: {downloaded}")
        print(f"      ❌ ناموفق: {failed}")
        print(f"      📁 مسیر: {year_dir}")

    def create_zip_artifact(self, base_dir: str, year: int) -> str:
        """ایجاد فایل ZIP از تصاویر یک سال برای دانلود به عنوان Artifact"""
        year_dir = os.path.join(base_dir, str(year))
        if not os.path.exists(year_dir):
            return None
        
        zip_filename = f"posters_{year}.zip"
        zip_path = os.path.join(base_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(year_dir):
                for file in files:
                    if file.endswith('.jpg'):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, base_dir)
                        zipf.write(file_path, arcname)
        
        print(f"   📦 فایل ZIP ساخته شد: {zip_path}")
        return zip_path

def main():
    ACCESS_TOKEN = os.environ.get('TMDB_ACCESS_TOKEN')
    
    if not ACCESS_TOKEN:
        print("❌ خطا: TMDB_ACCESS_TOKEN پیدا نشد!")
        print("   لطفاً توکن خود را در Secrets گیت‌هاب تنظیم کنید.")
        sys.exit(1)
    
    # دریافت سال از آرگومان‌ها
    if len(sys.argv) >= 2:
        year = int(sys.argv[1])
    else:
        year = datetime.now().year
        print(f"⚠️ سال مشخص نشد، استفاده از سال جاری: {year}")
    
    # مسیر خروجی
    output_dir = os.environ.get('POSTERS_OUTPUT_DIR', './downloaded_posters')
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n🎬 شروع دانلود پوستر فیلم‌های سال {year}")
    print(f"📁 مسیر ذخیره: {output_dir}/{year}")
    print(f"🔑 توکن TMDB: {'✓' if ACCESS_TOKEN else '✗'}")
    print("="*60)
    
    downloader = TMDBPosterDownloader(ACCESS_TOKEN)
    downloader.process_year(year, output_dir)
    
    # ایجاد ZIP برای آپلود Artifact
    zip_file = downloader.create_zip_artifact(output_dir, year)
    
    print(f"\n📊 آمار نهایی:")
    print(f"   🎬 کل فیلم‌های پردازش شده: {downloader.stats['total_movies']}")
    print(f"   🖼️ پوسترهای دانلود شده: {downloader.stats['downloaded_posters']}")
    print(f"   ❌ ناموفق: {downloader.stats['failed_posters']}")
    print(f"   🌐 درخواست‌های API: {downloader.stats['api_calls']}")
    
    # ذخیره گزارش JSON
    report = {
        'year': year,
        'stats': downloader.stats,
        'output_directory': output_dir,
        'timestamp': datetime.now().isoformat()
    }
    
    report_path = os.path.join(output_dir, f'report_{year}.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ فرآیند سال {year} کامل شد!")
    print(f"   📄 گزارش: {report_path}")
    if zip_file:
        print(f"   📦 فایل ZIP: {zip_file}")
        # چاپ مسیر ZIP برای GitHub Actions
        print(f"::set-output name=zip_path::{zip_file}")

if __name__ == "__main__":
    main()

import os
import shutil
import re

ext_map = {'.jpg': 'Images', '.jpeg': 'Images', '.png': 'Images', '.gif': 'Images', '.bmp': 'Images', '.tiff': 'Images', '.svg': 'Images', '.pdf': 'PDFs', '.doc': 'Documents', '.docx': 'Documents', '.txt': 'Documents', '.rtf': 'Documents', '.odt': 'Documents', '.xls': 'Spreadsheets', '.xlsx': 'Spreadsheets', '.csv': 'Spreadsheets', '.ods': 'Spreadsheets', '.ppt': 'Presentations', '.pptx': 'Presentations', '.odp': 'Presentations', '.mp4': 'Videos', '.mov': 'Videos', '.avi': 'Videos', '.mkv': 'Videos', '.wmv': 'Videos', '.mp3': 'Audio', '.wav': 'Audio', '.aac': 'Audio','.flac': 'Audio', '.ogg': 'Audio', '.zip': 'Archives', '.rar': 'Archives', '.tar': 'Archives', '.gz': 'Archives', '.7z': 'Archives', '.exe': 'Executables', '.msi': 'Executables', '.bat': 'Executables', '.sh': 'Executables', '.py': 'Python', '.java': 'Java', '.c': 'C', '.cpp': 'C++', '.html': 'HTML', '.css': 'CSS', '.js': 'JavaScript', '.php': 'PHP', '.rb': 'Ruby', '.swift': 'Swift', '.go': 'Go', '.rs': 'Rust', '.kt': 'Kotlin', '.dart': 'Dart', '.lua': 'Lua', '.pl': 'Perl', '.r': 'R', '.m': 'MATLAB', '.ps1': 'PowerShell', '.psm1': 'PowerShell Modules', '.psd1': 'PowerShell Data Files', '.ps1xml': 'PowerShell XML Files'}
dup_pattern = re.compile(r'\(\d+\)$')

def organize(dire):
  """
  Scans a directory and automatically sorts files into subfolders based on their extensions.

  Safely handles duplicate files by appending a numbered suffix to prevent data loss, 
  and isolates file-level errors to ensure continuous execution.

  Args:
      dire (str): The absolute path of the directory to be organized.
  """
  fset = set()
  with os.scandir(dire) as entries:
    for file in entries:
      try:
        if file.is_file():
          ext = os.path.splitext(file.name)[1].lower()
          folder = ext_map.get(ext,'Others')
          dest_folder_path = os.path.join(dire, folder)
          if dest_folder_path not in fset:
            os.makedirs(os.path.join(dire, folder), exist_ok=True)
            fset.add(dest_folder_path)
          dest_path = os.path.join(dire, folder, file.name)
          if os.path.exists(dest_path):
            base, ext = os.path.splitext(file.name)
            counter = 1
            while os.path.exists(dest_path):
              if dup_pattern.search(base):
                base = dup_pattern.sub('', base)
              dest_path = os.path.join(dire, folder, f"{base}({counter}){ext}")
              counter +=1
          shutil.move(file.path,dest_path)
          print('File: ',file.name,' -> Destination: ',folder)
      except Exception as e:
        print(f'Error : {e} while moving {file.name}')
        continue


def main():
  while True:
    dire = input('Enter the directory path:')
    try:
      if os.path.exists(dire) and os.path.isdir(dire):
        organize(dire)
        print('Files organized successfully')
        break
    except FileNotFoundError:
      print('Directory not found')
    except PermissionError:
      print('Permission denied')
    except Exception as e:
      print('An error occurred: ',e)


if __name__=='__main__':
  main()
import os
import sys
import shutil
import functools

def clean_extra_files(folder_path):
  def _clean_extra_files(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
      original_file_system_entries = os.listdir(folder_path)
      f(*args, **kwargs)
      final_file_system_entries = os.listdir(folder_path)

      extra_file_system_entries= filter_extra_files(original_file_system_entries, final_file_system_entries)
      for entry in extra_file_system_entries:
        delete_file_or_folder(entry, folder_path)
        
    return wrapper
  return _clean_extra_files

def filter_extra_files(original, final):
  is_not_original = lambda x : x not in original
  return list(filter(is_not_original, final))

def delete_file_or_folder(entry, folder_path):
  if os.path.isfile(os.path.join(folder_path, entry)):
    os.remove(os.path.join(folder_path, entry))
  else:
    shutil.rmtree(os.path.join(folder_path, entry), ignore_errors=True)



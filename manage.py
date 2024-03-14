#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import subprocess

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'users_admin.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Verificar si go2rtc.exe existe en el directorio actual
    go2rtc_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'go2rtc.exe')
    if not os.path.exists(go2rtc_path):
        print("Error: 'go2rtc.exe' not found in the directory.")
        return
    
    # Lanzar el archivo go2rtc.exe como un proceso independiente
    subprocess.Popen([go2rtc_path])
    
    # Ejecutar tareas administrativas de Django
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()

"""
Create desktop shortcut with custom icon for Head AI
"""
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw

def create_server_icon():
    """Create a server icon"""
    # Create resources directory if it doesn't exist
    resources_dir = Path('resources')
    resources_dir.mkdir(exist_ok=True)
    
    icon_path = resources_dir / 'server_icon.ico'
    if icon_path.exists():
        return str(icon_path.absolute())
        
    # Create base image
    size = (64, 64)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw server icon
    # Outer circle
    draw.ellipse([2, 2, 61, 61], outline='#00ff00', width=2)
    
    # Server shape
    draw.rectangle([22, 12, 42, 52], fill='#00ff00')
    draw.rectangle([25, 15, 39, 20], fill='#ffffff')
    draw.rectangle([25, 25, 39, 30], fill='#ffffff')
    
    # Save as ICO
    # First save as PNG
    png_path = resources_dir / 'server_icon.png'
    img.save(png_path)
    
    # Convert to ICO
    img.save(icon_path, format='ICO', sizes=[(64, 64)])
    
    return str(icon_path.absolute())

def create_desktop_shortcut():
    """Create desktop shortcut with custom icon"""
    try:
        # Create icon
        icon_path = create_server_icon()
        
        # Use OneDrive Desktop path
        desktop = Path(r'C:\Users\Andrei\OneDrive\Desktop')
        if not desktop.exists():
            print(f"Error: OneDrive Desktop path not found: {desktop}")
            return
            
        shortcut_path = desktop / 'Head AI Server.lnk'
        
        # Get absolute paths
        script_path = Path('launch_monitor.bat').absolute()
        
        # Create shortcut using PowerShell
        ps_script = f'''
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "{script_path}"
        $Shortcut.IconLocation = "{icon_path}"
        $Shortcut.WorkingDirectory = "{script_path.parent}"
        $Shortcut.Save()
        '''
        
        # Write PowerShell script to temp file
        ps_file = Path('create_shortcut.ps1')
        ps_file.write_text(ps_script)
        
        # Execute PowerShell script
        os.system(f'powershell -ExecutionPolicy Bypass -File "{ps_file}"')
        
        # Clean up
        ps_file.unlink()
        
        print(f"Desktop shortcut created successfully at: {shortcut_path}")
        print(f"Using icon: {icon_path}")
        
    except Exception as e:
        print(f"Error creating shortcut: {e}")

if __name__ == '__main__':
    create_desktop_shortcut()

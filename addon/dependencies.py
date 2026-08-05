"""
Dependency Management.

Checks for and installs required third-party Python packages (like classy_blocks
and PyVista) to ensure the add-on functions correctly in the local Blender Python env.
"""

# pyrefly: ignore [missing-import]
import bpy
import sys
import subprocess
import os
import platform
import tempfile
import shutil

def check_python_deps():
    """Returns True if required python packages are installed."""
    try:
        import classy_blocks
        import pyvista
        return True
    except ImportError:
        return False

def get_openfoam_status(context):
    """Returns True if the OpenFOAM bashrc exists.

    Args:
      context: 

    Returns:

    """
    try:
        bashrc_path = context.preferences.addons[__package__].preferences.bashrc_path
    except Exception:
        bashrc_path = ""
        
    if bashrc_path and os.path.exists(bashrc_path):
        return True
        
    # Check local fallback (symlink or directory in addon)
    addon_dir = os.path.dirname(os.path.abspath(__file__))
    for name in ["OpenFOAM-13", "openfoam13"]:
        local_bashrc = os.path.join(addon_dir, name, "etc", "bashrc")
        if os.path.exists(local_bashrc):
            return True
    return False


def _draw_startup_warning(self, context) -> None:
    """

    Args:
      context: 

    Returns:

    """
    self.layout.label(text="Classy Blocks is missing dependencies!", icon='ERROR')
    
    if not check_python_deps():
        self.layout.label(text="- Missing Python Packages (classy_blocks, pyvista)")
        
    try:
        if not get_openfoam_status(context):
            self.layout.label(text="- Missing OpenFOAM installation")
    except Exception:
        pass # Handle cases where context is restricted

    self.layout.separator()
    self.layout.label(text="Please check the 'ClassyMesh' panel in the 3D Viewport to install them.")


def _check_on_startup() -> None:
    """Runs exactly once after Blender starts up to warn the user."""
    # We delay execution by 1 second so the UI is fully ready to display a popup
    def delayed_popup():
        """ """
        has_py = check_python_deps()
        has_of = False
        try:
            has_of = get_openfoam_status(bpy.context)
        except Exception:
            pass
            
        if not has_py or not has_of:
            bpy.context.window_manager.popup_menu(
                _draw_startup_warning, 
                title="Classy Blocks Setup Required", 
                icon='ERROR'
            )
        return None # Returning None stops the timer
        
    bpy.app.timers.register(delayed_popup, first_interval=1.0)

@bpy.app.handlers.persistent
def _startup_handler(dummy) -> None:
    """

    Args:
      dummy: 

    Returns:

    """
    _check_on_startup()

def register_startup_checks() -> None:
    """ """
    if _startup_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_startup_handler)

def unregister_startup_checks() -> None:
    """ """
    if _startup_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_startup_handler)


class CLASSY_OT_install_python_deps(bpy.types.Operator):
    """ """
    bl_idname = "classy.install_python_deps"
    bl_label = "Install Python Dependencies"
    bl_description = "Installs classy_blocks, pyvista, and nptyping into Blender's Python"
    
    _timer = None
    _process = None

    def modal(self, context, event):
        """

        Args:
          context: 
          event: 

        Returns:

        """
        if event.type == 'TIMER':
            if self._process is not None:
                ret = self._process.poll()
                if ret is not None:
                    # Process finished
                    wm = context.window_manager
                    wm.event_timer_remove(self._timer)
                    
                    if ret == 0:
                        self.report({'INFO'}, "Successfully installed Python dependencies!")
                        def draw_success(self, context) -> None:
                            """

                            Args:
                              context: 

                            Returns:

                            """
                            self.layout.label(text="Dependencies installed successfully!", icon='CHECKMARK')
                        context.window_manager.popup_menu(draw_success, title="Installation Complete", icon='INFO')
                    else:
                        self.report({'ERROR'}, "Failed to install dependencies (Check console)")
                        def draw_error(self, context) -> None:
                            """

                            Args:
                              context: 

                            Returns:

                            """
                            self.layout.label(text="Installation failed! Check system console.", icon='ERROR')
                        context.window_manager.popup_menu(draw_error, title="Installation Failed", icon='ERROR')
                    
                    # Force UI redraw
                    for window in context.window_manager.windows:
                        for area in window.screen.areas:
                            area.tag_redraw()
                    return {'FINISHED'}
        return {'PASS_THROUGH'}

    def execute(self, context):
        """

        Args:
          context: 

        Returns:

        """
        self.report({'INFO'}, "Installing Python dependencies in background...")
        def draw_start(self, context) -> None:
            """

            Args:
              context: 

            Returns:

            """
            self.layout.label(text="Installing packages in the background...", icon='INFO')
            self.layout.label(text="This may take a minute. Please wait.")
        context.window_manager.popup_menu(draw_start, title="Installing Dependencies", icon='PACKAGE')
        
        # Combine commands into one python call so we manage one process
        cmd = [
            sys.executable, "-c", 
            "import subprocess, sys; "
            "subprocess.run([sys.executable, '-m', 'ensurepip']); "
            "subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip']); "
            "subprocess.run([sys.executable, '-m', 'pip', 'install', 'classy_blocks', 'pyvista'])"
        ]
        
        self._process = subprocess.Popen(cmd)
        
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}


class CLASSY_OT_install_openfoam(bpy.types.Operator):
    """ """
    bl_idname = "classy.install_openfoam"
    bl_label = "Install OpenFOAM"
    bl_description = "Attempts to install OpenFOAM for your operating system"
    
    def execute(self, context):
        """

        Args:
          context: 

        Returns:

        """
        os_name = platform.system()
        
        if os_name == "Windows":
            bpy.ops.wm.url_open(url="https://openfoam.org/download/windows/")
            self.report({'INFO'}, "Opened OpenFOAM Windows installation guide.")
            return {'FINISHED'}
            
        elif os_name == "Darwin":
            bpy.ops.wm.url_open(url="https://openfoam.org/download/mac/")
            self.report({'INFO'}, "Opened OpenFOAM Mac installation guide.")
            return {'FINISHED'}
            
        else: # Linux
            if shutil.which("apt-get"):
                # Ubuntu/Debian based
                script_path = os.path.join(tempfile.gettempdir(), "install_openfoam.sh")
                with open(script_path, "w") as f:
                    f.write("#!/bin/bash\n")
                    f.write("echo 'Installing OpenFOAM 13 for Ubuntu/Debian...'\n")
                    f.write("echo 'You may be prompted for your sudo password.'\n")
                    f.write("sudo sh -c 'wget -O - https://dl.openfoam.org/source/gpg.key | apt-key add -'\n")
                    f.write("sudo add-apt-repository -y http://dl.openfoam.org/ubuntu\n")
                    f.write("sudo apt-get update\n")
                    f.write("sudo apt-get -y install openfoam13\n")
                    
                    # Create symlink inside the Blender addon folder
                    addon_dir = os.path.dirname(os.path.abspath(__file__))
                    f.write("echo '\\n--- Creating symlink inside Blender Add-on ---'\n")
                    f.write(f"ln -sfn \"/opt/openfoam13\" \"{addon_dir}/OpenFOAM-13\"\n")
                    
                    f.write("echo 'Installation finished. Press Enter to close this window.'\n")
                    f.write("read\n")
                
                os.chmod(script_path, 0o755)
                
                terminals = ['x-terminal-emulator', 'gnome-terminal', 'konsole', 'xterm']
                for term in terminals:
                    if shutil.which(term):
                        if term == 'gnome-terminal':
                            subprocess.Popen([term, '--', 'bash', '-c', script_path])
                        else:
                            subprocess.Popen([term, '-e', script_path])
                        self.report({'INFO'}, f"Launched OpenFOAM installer via {term}.")
                        return {'FINISHED'}
                        
                # Fallback if no terminal
                bpy.ops.wm.url_open(url="https://openfoam.org/download/13-ubuntu/")
                self.report({'WARNING'}, "No terminal emulator found. Opened manual install guide.")
            else:
                # Other Linux distros (Fedora, Arch, etc.) - Build from source
                script_path = os.path.join(tempfile.gettempdir(), "install_openfoam_source.sh")
                with open(script_path, "w") as f:
                    f.write("#!/bin/bash\n")
                    f.write("set -e\n")
                    f.write("trap 'echo \"\\n[ERROR] Source compilation failed.\"; echo \"Opening official instructions...\"; xdg-open https://openfoam.org/download/source/ || true; echo \"Press Enter to close this window.\"; read dummy; exit 1' ERR\n\n")
                    f.write("echo '==================================================='\n")
                    f.write("echo '  Classy Blocks: OpenFOAM 13 Source Installer'\n")
                    f.write("echo '==================================================='\n")
                    f.write("echo 'Your Linux distribution is not Ubuntu/Debian.'\n")
                    f.write("echo 'Attempting to build OpenFOAM 13 from source...'\n")
                    f.write("echo 'WARNING: This will take a significant amount of time (often several hours).'\n")
                    f.write("echo 'You will be prompted for your sudo password to install prerequisites.'\n")
                    f.write("echo\n")
                    
                    f.write("# 1. Try to install generic dependencies based on package manager\n")
                    f.write("if command -v dnf &> /dev/null; then\n")
                    f.write("    sudo dnf install -y gcc gcc-c++ flex bison zlib-devel boost-devel openmpi openmpi-devel make cmake gmp-devel mpfr-devel wget tar\n")
                    f.write("elif command -v yum &> /dev/null; then\n")
                    f.write("    sudo yum install -y gcc gcc-c++ flex bison zlib-devel boost-devel openmpi openmpi-devel make cmake gmp-devel mpfr-devel wget tar\n")
                    f.write("elif command -v pacman &> /dev/null; then\n")
                    f.write("    sudo pacman -Sy --noconfirm base-devel flex bison zlib boost openmpi cmake gmp mpfr wget tar\n")
                    f.write("elif command -v zypper &> /dev/null; then\n")
                    f.write("    sudo zypper install -y gcc gcc-c++ flex bison zlib-devel boost-devel openmpi-devel cmake gmp-devel mpfr-devel wget tar\n")
                    f.write("else\n")
                    f.write("    echo 'Warning: Unsupported package manager. Make sure build dependencies (gcc, flex, bison, zlib, boost, openmpi, cmake) are installed manually.'\n")
                    f.write("fi\n\n")
                    
                    f.write("# 2. Download and Extract\n")
                    f.write("FOAM_DIR=\"$HOME/OpenFOAM\"\n")
                    f.write("mkdir -p \"$FOAM_DIR\"\n")
                    f.write("cd \"$FOAM_DIR\"\n")
                    f.write("echo '\\n--- Downloading OpenFOAM 13 Source ---'\n")
                    f.write("wget -O OpenFOAM-13.tgz \"https://github.com/OpenFOAM/OpenFOAM-13/archive/version-13.tar.gz\"\n")
                    f.write("wget -O ThirdParty-13.tgz \"https://github.com/OpenFOAM/ThirdParty-13/archive/version-13.tar.gz\"\n")
                    
                    f.write("echo '\\n--- Extracting Archives ---'\n")
                    f.write("tar -xzf OpenFOAM-13.tgz\n")
                    f.write("tar -xzf ThirdParty-13.tgz\n")
                    f.write("rm -rf OpenFOAM-13 ThirdParty-13 || true\n")
                    f.write("mv OpenFOAM-13-* OpenFOAM-13\n")
                    f.write("mv ThirdParty-13-* ThirdParty-13\n\n")
                    
                    f.write("# Patch ThirdParty for Fedora/GCC 16\n")
                    f.write("sed -i 's/-Drestrict=__restrict/-Drestrict=__restrict -std=gnu89/g' ThirdParty-13/etc/wmakeFiles/scotch/Makefile.inc.i686_pc_linux2.shlib-OpenFOAM\n")
                    f.write("sed -i 's/--with-mpi-libdir=\\$MPI_ARCH_PATH\\/lib\\${WM_COMPILER_LIB_ARCH} \\\\/--with-mpi-libdir=\\$MPI_ARCH_PATH\\/lib \\\\\\n                --with-mpi-incdir=\\/usr\\/include\\/openmpi-x86_64 \\\\/g' ThirdParty-13/Allwmake\n\n")
                    
                    f.write("# 3. Compile\n")
                    f.write("echo '\\n--- Starting Compilation (This will take a long time!) ---'\n")
                    f.write("# Add OpenMPI path for Fedora/RHEL if present\n")
                    f.write("if [ -d \"/usr/lib64/openmpi/bin\" ]; then\n")
                    f.write("    export PATH=\"/usr/lib64/openmpi/bin:$PATH\"\n")
                    f.write("fi\n")
                    f.write("source \"$FOAM_DIR/OpenFOAM-13/etc/bashrc\" || true\n")
                    f.write("cd \"$FOAM_DIR/OpenFOAM-13\"\n")
                    f.write("export WM_NCOMPPROCS=$(nproc)\n")
                    f.write("./Allwmake -j $(nproc)\n\n")
                    
                    # Create symlink inside the Blender addon folder
                    addon_dir = os.path.dirname(os.path.abspath(__file__))
                    f.write("echo '\\n--- Creating symlink inside Blender Add-on ---'\n")
                    f.write(f"ln -sfn \"$FOAM_DIR/OpenFOAM-13\" \"{addon_dir}/OpenFOAM-13\"\n")
                    
                    f.write("echo '\\n==================================================='\n")
                    f.write("echo '  Compilation and setup finished successfully!'\n")
                    f.write("echo '==================================================='\n")
                    f.write("echo 'OpenFOAM 13 has been symlinked directly into your Blender addon!'\n")
                    f.write("echo 'You do not need to manually configure bashrc path; it will use the symlink.'\n")
                    f.write("echo\n")
                    f.write("echo 'Press Enter to close this window...'\n")
                    f.write("read dummy\n")
                    
                os.chmod(script_path, 0o755)
                
                terminals = ['x-terminal-emulator', 'gnome-terminal', 'konsole', 'xterm']
                launched = False
                for term in terminals:
                    if shutil.which(term):
                        if term == 'gnome-terminal':
                            subprocess.Popen([term, '--', 'bash', '-c', script_path])
                        else:
                            subprocess.Popen([term, '-e', script_path])
                        self.report({'INFO'}, f"Launched OpenFOAM source installer via {term}.")
                        launched = True
                        break
                
                if not launched:
                    bpy.ops.wm.url_open(url="https://openfoam.org/download/source/")
                    self.report({'WARNING'}, "No terminal emulator found. Opened manual source install guide.")
                    
            return {'FINISHED'}

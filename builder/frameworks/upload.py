from platformio.public import list_serial_ports
from frameworks.uf2conv import dev_uploader
from os.path import join

def BeforeUpload(target, source, env):  # pylint: disable=W0613,W0621
    upload_options = {}
    if "BOARD" in env:
        upload_options = env.BoardConfig().get("upload", {})

    env.AutodetectUploadPort()
    before_ports = list_serial_ports()

    if upload_options.get("use_1200bps_touch", False):
        env.TouchSerialPort("$UPLOAD_PORT", 1200)

    if upload_options.get("wait_for_upload_port", False):
        env.Replace(UPLOAD_PORT=env.WaitForNewSerialPort(before_ports))

def upload(env, prg):
    upload_protocol = env.subst("$UPLOAD_PROTOCOL") or "uf2"
    
    if upload_protocol == "uf2":
        env.Replace(UPLOADCMD = dev_uploader)
        return env.Alias("upload", prg, [ 
            env.VerboseAction("$UPLOADCMD", "Uploading..."),
            env.VerboseAction("", "")
        ])
    
    elif upload_protocol == "picotool":
        platform = platform = env.PioPlatform()
        rp2040tools = platform.get_package_dir("tool-rp2040tools")
        elf2uf2 = join(rp2040tools or "", "elf2uf2")
        upload_source="$BUILD_DIR/${PROGNAME}.uf2"
        env.Execute(elf2uf2 + " $BUILD_DIR/${PROGNAME}.elf ${upload_source}")
        env.Replace(
            UPLOADER=join(rp2040tools or "", "rp2040load"),
            UPLOADERFLAGS=["-v", "-D"],
            #UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS $SOURCES'
            UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS $BUILD_DIR/${PROGNAME}'
            
        )

        #upload_source="$BUILD_DIR/${PROGNAME}.uf2"
        
        return env.Alias("upload", prg, [ 
            env.VerboseAction(BeforeUpload, "Looking for upload port..."),
            env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE"),
        ])
    
        #AlwaysBuild(env.Alias("upload", upload_source, upload_actions))
    
